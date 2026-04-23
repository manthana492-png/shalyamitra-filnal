"""
ShalyaMitra — TTS Router

Routes text-to-speech requests to the correct TTS engine:

  1. Critical Alert Path → Piper TTS (CPU, <50ms) or pre-recorded .wav
  2. Conversational Path → Fish Speech 1.5 (GPU, ~200-300ms)
  3. Fallback → OpenRouter/Gemini TTS API (cloud, ~400-600ms)
  4. Last resort → Browser-side Web Speech API (frontend handles this)

The router also selects the correct voice profile based on:
  - Which pillar is speaking
  - Alert severity level
  - Surgeon's voice preference
"""

from __future__ import annotations

import asyncio
import base64
import time
from dataclasses import dataclass
from enum import Enum
from typing import Optional

import httpx

from app.config import settings
from app.agents.voice_profiles import get_voice_manager, VoiceProfile, VoiceCategory


class TTSEngine(str, Enum):
    """Available TTS engines in priority order."""
    PIPER = "piper"                 # Critical alerts only — CPU, ultra-fast
    FISH_SPEECH = "fish_speech"     # Primary conversational — GPU
    OPENROUTER = "openrouter"       # Fallback 1 — cloud API
    BROWSER = "browser"             # Fallback 2 — client-side Web Speech API


@dataclass
class TTSResult:
    """Result from TTS synthesis."""
    audio_b64: str              # base64-encoded audio
    mime_type: str              # "audio/wav" or "audio/mp3"
    engine_used: TTSEngine      # Which engine actually produced this
    voice_id: str               # Which voice profile was used
    latency_ms: float           # How long synthesis took
    is_fallback: bool           # Whether a fallback engine was used


# ══════════════════════════════════════════════════════════
# Pre-recorded Alert Templates
# ══════════════════════════════════════════════════════════

# These are text templates for common critical alerts.
# In production, we pre-generate .wav files for each template
# at system startup using Piper, so they play instantly (<10ms).
PRERECORDED_ALERTS: dict[str, str] = {
    "haemorrhage_arterial": "ALERT. Possible arterial bleed detected. Camera expanded.",
    "haemorrhage_venous": "ALERT. Venous bleeding detected in surgical field.",
    "haemorrhage_general": "ALERT. Bleeding detected. Haemorrhage sentinel activated.",
    "spo2_critical": "ALERT. Oxygen saturation critical. Check airway immediately.",
    "hr_bradycardia": "ALERT. Heart rate critically low. Bradycardia detected.",
    "hr_tachycardia": "ALERT. Heart rate critically high. Tachycardia detected.",
    "map_hypotension": "ALERT. Severe hypotension. Consider vasopressors.",
    "instrument_mismatch": "ALERT. Instrument count discrepancy. Verify all instruments.",
    "retraction_limit": "Retraction time limit reached. Consider releasing retractor.",
}

# In-memory cache of pre-generated alert audio
_prerecorded_cache: dict[str, str] = {}  # template_key → base64 wav


class TTSRouter:
    """
    Routes TTS requests through the engine cascade with automatic fallback.

    Engine selection:
      - severity=critical → Piper (or pre-recorded) — NEVER waits for GPU
      - severity=warning  → Piper
      - normal speech     → Fish Speech → OpenRouter fallback → browser fallback
    """

    def __init__(self):
        self._http: Optional[httpx.AsyncClient] = None
        self._fish_healthy = True
        self._piper_healthy = True
        self._last_health_check = 0.0

    async def _get_http(self) -> httpx.AsyncClient:
        if self._http is None or self._http.is_closed:
            self._http = httpx.AsyncClient(timeout=10.0)
        return self._http

    async def synthesize(
        self,
        text: str,
        pillar: str = "nael",
        severity: str = "info",
        voice_override: Optional[str] = None,
    ) -> TTSResult:
        """
        Synthesize speech with automatic engine selection and fallback.

        Args:
            text: The text to speak
            pillar: Which intelligence pillar is speaking
            severity: Alert severity (affects engine selection)
            voice_override: Force a specific voice profile ID
        """
        start = time.monotonic()
        voice_mgr = get_voice_manager()

        # Resolve voice profile
        if voice_override:
            voice = voice_mgr.profiles.get(voice_override,
                        voice_mgr.resolve_voice(pillar, severity))
        else:
            voice = voice_mgr.resolve_voice(pillar, severity)

        # ── Critical Alert Path: Piper or pre-recorded ───
        if severity in ("critical", "warning"):
            result = await self._critical_path(text, voice, start)
            if result:
                return result
            # If Piper fails, fall through to Fish Speech

        # ── Primary: Fish Speech 1.5 ─────────────────────
        if self._fish_healthy:
            result = await self._try_fish_speech(text, voice, start)
            if result:
                return result

        # ── Fallback 1: OpenRouter / Gemini Flash TTS ────
        result = await self._try_openrouter_tts(text, voice, start)
        if result:
            return result

        # ── Fallback 2: Return text for browser synthesis ─
        return self._browser_fallback(text, voice, start)

    # ──────────────────────────────────────────────────────
    # Engine Implementations
    # ──────────────────────────────────────────────────────

    async def _critical_path(self, text: str, voice: VoiceProfile,
                              start: float) -> Optional[TTSResult]:
        """
        Critical Alert Path — ultra-low latency.
        Checks pre-recorded cache first, then uses Piper TTS.
        """
        # Check pre-recorded cache
        for key, template in PRERECORDED_ALERTS.items():
            if template.lower() in text.lower() or text.lower() in template.lower():
                if key in _prerecorded_cache:
                    return TTSResult(
                        audio_b64=_prerecorded_cache[key],
                        mime_type="audio/wav",
                        engine_used=TTSEngine.PIPER,
                        voice_id="prerecorded_" + key,
                        latency_ms=0.5,  # Essentially instant
                        is_fallback=False,
                    )

        # Try Piper TTS
        if self._piper_healthy:
            try:
                http = await self._get_http()
                resp = await http.post(
                    f"{settings.piper_url}/api/tts",
                    json={"text": text, "output_type": "wav"},
                    timeout=2.0,  # Strict timeout for critical path
                )
                if resp.status_code == 200:
                    audio_b64 = base64.b64encode(resp.content).decode("utf-8")
                    elapsed = (time.monotonic() - start) * 1000
                    return TTSResult(
                        audio_b64=audio_b64,
                        mime_type="audio/wav",
                        engine_used=TTSEngine.PIPER,
                        voice_id=voice.id,
                        latency_ms=elapsed,
                        is_fallback=False,
                    )
            except Exception:
                self._piper_healthy = False
                # Schedule health re-check in 30s
                asyncio.get_event_loop().call_later(30, self._reset_piper_health)

        return None

    async def _try_fish_speech(self, text: str, voice: VoiceProfile,
                                start: float) -> Optional[TTSResult]:
        """
        Fish Speech 1.5 — primary conversational TTS.
        Uses voice cloning with reference audio for the selected voice profile.
        """
        try:
            http = await self._get_http()

            # Build request
            payload: dict = {
                "text": text,
                "format": "wav",
                "streaming": False,
            }

            # Add reference audio for voice cloning if available
            ref_audio = get_voice_manager().get_reference_audio(voice.id)
            if ref_audio:
                payload["reference_audio"] = ref_audio

            resp = await http.post(
                f"{settings.fish_speech_url}/v1/tts",
                json=payload,
                timeout=8.0,
            )

            if resp.status_code == 200:
                audio_b64 = base64.b64encode(resp.content).decode("utf-8")
                elapsed = (time.monotonic() - start) * 1000
                return TTSResult(
                    audio_b64=audio_b64,
                    mime_type="audio/wav",
                    engine_used=TTSEngine.FISH_SPEECH,
                    voice_id=voice.id,
                    latency_ms=elapsed,
                    is_fallback=False,
                )
        except Exception:
            self._fish_healthy = False
            asyncio.get_event_loop().call_later(60, self._reset_fish_health)

        return None

    async def _try_openrouter_tts(self, text: str, voice: VoiceProfile,
                                   start: float) -> Optional[TTSResult]:
        """
        Fallback TTS via OpenRouter — uses Gemini Flash or other
        audio-capable models.

        Strategy:
          1. Try Google Gemini 2.0 Flash (free tier) for text-to-audio
          2. Try OpenAI TTS via OpenRouter
          3. Give up and fall to browser
        """
        if not settings.openrouter_api_key:
            return None

        try:
            http = await self._get_http()

            # ── Attempt 1: Gemini 2.0 Flash (audio output) ───
            # Gemini can generate audio natively via the multimodal API
            resp = await http.post(
                f"{settings.openrouter_base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.openrouter_api_key}",
                    "HTTP-Referer": "https://shalyamitra.dev",
                    "X-Title": "ShalyaMitra Surgical AI",
                },
                json={
                    "model": "google/gemini-2.0-flash-001",
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "You are a surgical AI assistant voice. "
                                "Speak the following text clearly and professionally. "
                                "Do not add any extra words."
                            ),
                        },
                        {"role": "user", "content": f"Speak this exactly: {text}"},
                    ],
                    # Request audio output modality
                    "modalities": ["text", "audio"],
                    "audio": {"voice": "alloy", "format": "wav"},
                },
                timeout=8.0,
            )

            if resp.status_code == 200:
                data = resp.json()
                # Extract audio from response
                audio_content = None

                # Check for audio in the response
                choices = data.get("choices", [])
                if choices:
                    message = choices[0].get("message", {})
                    audio_data = message.get("audio", {})
                    if audio_data and "data" in audio_data:
                        audio_content = audio_data["data"]

                if audio_content:
                    elapsed = (time.monotonic() - start) * 1000
                    return TTSResult(
                        audio_b64=audio_content,
                        mime_type="audio/wav",
                        engine_used=TTSEngine.OPENROUTER,
                        voice_id="gemini_flash_alloy",
                        latency_ms=elapsed,
                        is_fallback=True,
                    )

            # ── Attempt 2: OpenAI TTS via OpenRouter ─────────
            resp2 = await http.post(
                f"{settings.openrouter_base_url}/audio/speech",
                headers={
                    "Authorization": f"Bearer {settings.openrouter_api_key}",
                    "HTTP-Referer": "https://shalyamitra.dev",
                    "X-Title": "ShalyaMitra Surgical AI",
                },
                json={
                    "model": "openai/tts-1",
                    "input": text,
                    "voice": "nova",  # Clear, professional
                    "response_format": "wav",
                },
                timeout=8.0,
            )

            if resp2.status_code == 200:
                audio_b64 = base64.b64encode(resp2.content).decode("utf-8")
                elapsed = (time.monotonic() - start) * 1000
                return TTSResult(
                    audio_b64=audio_b64,
                    mime_type="audio/wav",
                    engine_used=TTSEngine.OPENROUTER,
                    voice_id="openai_tts_nova",
                    latency_ms=elapsed,
                    is_fallback=True,
                )

        except Exception:
            pass  # Fall through to browser

        return None

    def _browser_fallback(self, text: str, voice: VoiceProfile,
                           start: float) -> TTSResult:
        """
        Last resort — return empty audio with the text, signaling
        the frontend to use its built-in Web Speech API (speechSynthesis).
        """
        elapsed = (time.monotonic() - start) * 1000
        return TTSResult(
            audio_b64="",  # Empty = frontend should use browser TTS
            mime_type="text/plain",
            engine_used=TTSEngine.BROWSER,
            voice_id="browser_default",
            latency_ms=elapsed,
            is_fallback=True,
        )

    # ── Health management ─────────────────────────────────

    def _reset_fish_health(self):
        self._fish_healthy = True

    def _reset_piper_health(self):
        self._piper_healthy = True

    async def pregenerate_alerts(self):
        """
        Pre-generate all critical alert audio at system startup.
        Called during session initialization so alerts play instantly.
        """
        global _prerecorded_cache

        for key, template_text in PRERECORDED_ALERTS.items():
            if key in _prerecorded_cache:
                continue  # Already cached

            # Try Piper first
            result = await self._critical_path(template_text,
                        get_voice_manager().profiles.get("alert_urgent",
                            get_voice_manager().profiles["nael_calm"]),
                        time.monotonic())
            if result and result.audio_b64:
                _prerecorded_cache[key] = result.audio_b64
                continue

            # Try Fish Speech
            result = await self._try_fish_speech(template_text,
                        get_voice_manager().profiles.get("alert_urgent",
                            get_voice_manager().profiles["nael_calm"]),
                        time.monotonic())
            if result and result.audio_b64:
                _prerecorded_cache[key] = result.audio_b64

    async def close(self):
        if self._http and not self._http.is_closed:
            await self._http.aclose()


# Singleton
_router: Optional[TTSRouter] = None


def get_tts_router() -> TTSRouter:
    global _router
    if _router is None:
        _router = TTSRouter()
    return _router
