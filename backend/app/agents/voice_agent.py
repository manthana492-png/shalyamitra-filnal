"""
ShalyaMitra — Voice Agent (Nael)

The orchestrating voice agent. Handles the full conversational loop:

  1. Wake word detected ("Nael")
  2. ASR transcribes surgeon's speech
  3. LLM reasons about the query (NIM local / OpenRouter cloud)
  4. TTS synthesizes the response (Fish Speech / Piper / fallback)
  5. Audio streams back to neckband

This agent does NOT handle critical alerts — those bypass the LLM
entirely via the Haemorrhage/Monitor agents' Critical Alert Path.

LLM routing:
  - During surgery: Nemotron 3 Super via NIM (self-hosted, ~400ms)
  - Pre/post surgery: Claude/GPT via OpenRouter (cloud, ~800ms)
  - Fallback: Gemini Flash via OpenRouter (free tier)
"""

from __future__ import annotations

import time
from typing import Any, Optional

import httpx

from app.config import settings
from app.agents.orchestrator import BaseAgent, AgentEvent, EventType
from app.agents.asr_pipeline import get_asr_pipeline, ASRResult
from app.agents.tts_router import get_tts_router, TTSResult
from app.agents.wake_word import get_wake_word_detector, WakeWordResult, WakeWordType
from app.agents.voice_profiles import get_voice_manager


class VoiceAgent(BaseAgent):
    """
    Nael — The Voice. Conversational surgical companion.

    State machine:
      IDLE → (wake word) → LISTENING → (speech ends) → THINKING → SPEAKING → IDLE

    The surgeon hears Nael's state transitions through subtle audio cues
    (soft chime on activation, thinking indicator tone).
    """

    def __init__(self):
        super().__init__(agent_id="voice_nael", pillar="nael")
        self._state = "idle"
        self._http: Optional[httpx.AsyncClient] = None
        self._conversation_history: list[dict] = []
        self._session_context: dict[str, Any] = {}

    @property
    def subscriptions(self) -> list[EventType]:
        return [
            EventType.TRANSCRIPT,       # ASR output
            EventType.WAKE_WORD,         # Wake word detection
            EventType.SESSION_START,     # Initialize conversation
            EventType.SESSION_END,       # Generate summary
            EventType.PHASE_CHANGE,      # Update phase context
            EventType.ALERT,             # Be aware of alerts
        ]

    async def _get_http(self) -> httpx.AsyncClient:
        if self._http is None or self._http.is_closed:
            self._http = httpx.AsyncClient(timeout=15.0)
        return self._http

    async def on_session_start(self, session_id: str):
        self._state = "idle"
        self._conversation_history = []
        self._session_context = {
            "session_id": session_id,
            "phase": "preparation",
            "procedure": "",
            "recent_alerts": [],
        }

    async def handle_event(self, event: AgentEvent) -> list[AgentEvent]:
        results: list[AgentEvent] = []

        if event.type == EventType.SESSION_START:
            # Greet the surgeon
            greeting = await self._generate_greeting(event.session_id)
            results.extend(greeting)
            return results

        if event.type == EventType.PHASE_CHANGE:
            self._session_context["phase"] = event.data.get("phase", "")
            return []

        if event.type == EventType.ALERT:
            # Track recent alerts for context
            self._session_context.setdefault("recent_alerts", []).append({
                "title": event.data.get("title", ""),
                "severity": event.data.get("severity", ""),
                "at": event.data.get("at", 0),
            })
            # Keep only last 10
            self._session_context["recent_alerts"] = \
                self._session_context["recent_alerts"][-10:]
            return []

        if event.type == EventType.WAKE_WORD:
            return await self._handle_wake_word(event)

        if event.type == EventType.TRANSCRIPT:
            return await self._handle_transcript(event)

        return results

    async def _handle_wake_word(self, event: AgentEvent) -> list[AgentEvent]:
        """Handle wake word detection."""
        ww_type = event.data.get("word_type", "activate")
        results: list[AgentEvent] = []

        if ww_type == "activate":
            self._state = "listening"
            results.append(AgentEvent(
                type=EventType.DISPLAY_TRANSCRIPT,
                source=self.agent_id,
                priority=6,
                session_id=event.session_id,
                data={"speaker": "system", "text": "Nael is listening...", "at": event.timestamp},
            ))

        elif ww_type == "deactivate":
            self._state = "idle"

        elif ww_type == "acknowledge":
            results.append(AgentEvent(
                type=EventType.DISPLAY_TRANSCRIPT,
                source=self.agent_id,
                priority=6,
                session_id=event.session_id,
                data={"speaker": "nael", "text": "Acknowledged.", "at": event.timestamp, "pillar": "nael"},
            ))

        return results

    async def _handle_transcript(self, event: AgentEvent) -> list[AgentEvent]:
        """Handle incoming transcript — run through the conversational pipeline."""
        text = event.data.get("text", "")
        speaker = event.data.get("speaker", "unknown")

        if not text or self._state != "listening":
            return []

        if speaker == "nael" or speaker == "system":
            return []  # Don't respond to ourselves

        # Transition: LISTENING → THINKING
        self._state = "thinking"
        results: list[AgentEvent] = []

        # Emit state change
        results.append(AgentEvent(
            type=EventType.DISPLAY_TRANSCRIPT,
            source=self.agent_id, priority=7,
            session_id=event.session_id,
            data={"speaker": "system", "text": "Nael is thinking...", "at": event.timestamp},
        ))

        # Generate LLM response
        response_text = await self._reason(text, event.session_id)

        if response_text:
            # Transition: THINKING → SPEAKING
            self._state = "speaking"

            # Emit transcript
            results.append(AgentEvent(
                type=EventType.DISPLAY_TRANSCRIPT,
                source=self.agent_id, priority=6,
                session_id=event.session_id,
                data={"speaker": "nael", "text": response_text, "at": event.timestamp, "pillar": "nael"},
            ))

            # Synthesize TTS
            tts = get_tts_router()
            tts_result = await tts.synthesize(response_text, pillar="nael")

            if tts_result.audio_b64:
                results.append(AgentEvent(
                    type=EventType.DISPLAY_TTS,
                    source=self.agent_id, priority=6,
                    session_id=event.session_id,
                    data={
                        "audioBase64": tts_result.audio_b64,
                        "mimeType": tts_result.mime_type,
                        "at": event.timestamp,
                        "engine": tts_result.engine_used.value,
                        "voice": tts_result.voice_id,
                    },
                ))

        # Back to idle
        self._state = "idle"
        return results

    async def _reason(self, query: str, session_id: Optional[str] = None) -> str:
        """
        Generate a reasoned response via NVIDIA NIM API.

        Uses PrivacyRouter which handles:
          1. PHI redaction (strips patient data before cloud call)
          2. Tier routing: Nemotron 49B → Kimi k2.5 → Gemini Flash
          3. Audit logging for every request
        """
        from app.safety.privacy_router import get_privacy_router
        from app.agents.surgical_memory import get_cortex

        system_prompt = self._build_system_prompt()

        # Add surgical context from cortex
        cortex = get_cortex()
        if cortex.started_at:
            clinical_ctx = cortex.build_clinical_context(500)
            system_prompt += f"\n\nCurrent clinical context:\n{clinical_ctx}"

        # Add to conversation history
        self._conversation_history.append({"role": "user", "content": query})
        if len(self._conversation_history) > 20:
            self._conversation_history = self._conversation_history[-20:]

        messages = [{"role": "system", "content": system_prompt}] + self._conversation_history

        # Route through NIM API (PHI stripped automatically)
        router = get_privacy_router()
        result = await router.infer(messages, agent_type="VoiceAgent",
                                    max_tokens=200, temperature=0.3)

        if result and "error" not in result:
            try:
                response = result["choices"][0]["message"]["content"].strip()
                self._conversation_history.append({"role": "assistant", "content": response})
                return response
            except (KeyError, IndexError):
                pass

        return "I'm having trouble connecting to my reasoning engine. Please try again."

    def _build_system_prompt(self) -> str:
        phase = self._session_context.get("phase", "preparation")
        alerts = self._session_context.get("recent_alerts", [])

        alert_context = ""
        if alerts:
            recent = alerts[-3:]
            alert_context = "\nRecent alerts: " + "; ".join(
                f"[{a['severity']}] {a['title']}" for a in recent
            )

        return f"""You are Nael, the voice of ShalyaMitra - a surgical intelligence companion.

CORE LAW: The surgeon must never break flow. Your responses must be:
- BRIEF (1-3 sentences max)
- PRECISE (use exact clinical terminology)
- ACTIONABLE (provide specific information, not vague advice)
- RESPECTFUL (you are a companion, not an authority)

You are currently in the {phase} phase of surgery.{alert_context}

Rules:
- Never diagnose. Never prescribe. You are a Clinical Decision SUPPORT tool.
- If asked about something outside your knowledge, say so immediately.
- When citing Ayurvedic references, provide the Shloka and modern mapping.
- Always acknowledge the surgeon's expertise — they decide, you inform.
- Keep responses under 30 words unless specifically asked to elaborate."""

    async def _generate_greeting(self, session_id: Optional[str]) -> list[AgentEvent]:
        """Generate the session opening greeting."""
        greeting = (
            "Good morning. Pre-operative analysis loaded. "
            "I'm here when you need me."
        )
        tts = get_tts_router()
        tts_result = await tts.synthesize(greeting, pillar="nael")

        results = [
            AgentEvent(
                type=EventType.DISPLAY_TRANSCRIPT,
                source=self.agent_id, priority=7,
                data={"speaker": "nael", "text": greeting, "at": 0, "pillar": "nael"},
            ),
        ]

        if tts_result.audio_b64:
            results.append(AgentEvent(
                type=EventType.DISPLAY_TTS,
                source=self.agent_id, priority=7,
                data={
                    "audioBase64": tts_result.audio_b64,
                    "mimeType": tts_result.mime_type, "at": 0,
                },
            ))

        return results
