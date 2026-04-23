"""
ShalyaMitra — Consultant Agent (The Consultant)

On-demand expert consultation during surgery:
  - Answers complex clinical queries using powerful LLMs
  - Provides differential diagnosis assistance
  - Suggests management strategies for complications
  - Can reason about unusual findings

Uses: OpenRouter (Claude 3.5 / GPT-4.1 / Gemini Pro) for deep reasoning.
"""

from __future__ import annotations
from typing import Any, Optional
import httpx, time
from app.agents.orchestrator import BaseAgent, AgentEvent, EventType
from app.config import settings


class ConsultantAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_id="consultant", pillar="consultant")
        self._http: Optional[httpx.AsyncClient] = None
        self._session_context: str = ""
        self._query_count: int = 0

    @property
    def subscriptions(self) -> list[EventType]:
        return [EventType.TRANSCRIPT, EventType.SESSION_START]

    async def _get_http(self) -> httpx.AsyncClient:
        if self._http is None or self._http.is_closed:
            self._http = httpx.AsyncClient(timeout=20.0)
        return self._http

    async def handle_event(self, event: AgentEvent) -> list[AgentEvent]:
        if event.type == EventType.SESSION_START:
            self._session_context = (
                f"Procedure: {event.data.get('procedure', 'N/A')}. "
                f"Patient: {event.data.get('patient', {}).get('age', 'N/A')}yo, "
                f"ASA {event.data.get('patient', {}).get('asa', 'N/A')}."
            )
            self._query_count = 0
            return []

        if event.type == EventType.TRANSCRIPT:
            text = event.data.get("text", "").lower()
            # Activated by keyword
            if any(kw in text for kw in ["consult", "second opinion", "what do you think",
                                          "differential", "management", "what would you do",
                                          "complicated", "unusual", "never seen"]):
                return await self._consult(event)
        return []

    async def _consult(self, event: AgentEvent) -> list[AgentEvent]:
        query = event.data.get("text", "")
        self._query_count += 1

        prompt = f"""You are a senior surgical consultant providing an expert second opinion.

Context: {self._session_context}
Surgeon's query: {query}

Rules:
- Be concise (3-5 sentences max)
- Provide specific, actionable advice
- If the situation is ambiguous, state the most likely scenario AND the worst-case to rule out
- Always acknowledge uncertainty where it exists
- Reference relevant guidelines (NICE, ACS, SAGES) when applicable
- End with a clear recommendation

IMPORTANT: You are a decision SUPPORT tool. Frame responses as suggestions, not directives."""

        response = await self._call_llm(prompt)

        return [AgentEvent(
            type=EventType.DISPLAY_TRANSCRIPT,
            source=self.agent_id, priority=5,
            session_id=event.session_id,
            data={
                "speaker": "consultant", "pillar": "consultant", "at": time.time(),
                "text": response or "Consulting... please repeat your query.",
            },
        )]

    async def _call_llm(self, prompt: str) -> Optional[str]:
        if not settings.openrouter_api_key:
            return "Consultant unavailable — no API key configured."
        try:
            http = await self._get_http()
            # Use the most capable model for consultation
            models = [settings.scholar_model, "google/gemini-2.0-flash-001"]
            for model in models:
                try:
                    resp = await http.post(
                        f"{settings.openrouter_base_url}/chat/completions",
                        headers={"Authorization": f"Bearer {settings.openrouter_api_key}",
                                 "HTTP-Referer": "https://shalyamitra.dev",
                                 "X-Title": "ShalyaMitra Consultant"},
                        json={"model": model,
                              "messages": [{"role": "user", "content": prompt}],
                              "max_tokens": 300, "temperature": 0.3},
                        timeout=12.0,
                    )
                    if resp.status_code == 200:
                        return resp.json()["choices"][0]["message"]["content"].strip()
                except Exception:
                    continue
        except Exception:
            pass
        return None
