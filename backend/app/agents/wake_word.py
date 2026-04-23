"""
ShalyaMitra — Wake Word Detection ("Nael")

Detects the wake word "Nael" to activate conversational mode.
Without the wake word, Nael listens but does NOT respond to
general conversation — only to direct invocations.

This prevents accidental AI activation during clinical dialogue
(e.g. surgeon discussing something with the anaesthetist should
NOT trigger Nael unless they specifically say "Nael").

3-tier implementation:
  1. NVIDIA Riva KWS (Keyword Spotting) — <50ms, on GPU
  2. OpenWakeWord (open-source, CPU) — <100ms, self-hosted
  3. Text-based detection from ASR transcript — ~200ms, fallback

Additional keywords:
  - "Nael" → activate conversational mode
  - "Nael stop" / "Nael quiet" → deactivate
  - "Alert acknowledged" / "Nael acknowledge" → acknowledge latest alert
  - "Nael show [x]" → display command
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from app.config import settings


class WakeWordEngine(str, Enum):
    RIVA_KWS = "riva_kws"
    OPENWAKEWORD = "openwakeword"
    TEXT_MATCH = "text_match"


class WakeWordType(str, Enum):
    ACTIVATE = "activate"           # "Nael" — start listening
    DEACTIVATE = "deactivate"       # "Nael stop" — stop listening
    ACKNOWLEDGE = "acknowledge"     # "Acknowledge" — ack alert
    MUTE = "mute"                   # "Nael mute" — mute audio
    UNMUTE = "unmute"               # "Nael unmute"
    END = "end"                     # "Nael end session"
    COMMAND = "command"             # "Nael show/focus/overlay..."


@dataclass
class WakeWordResult:
    """Result from wake word detection."""
    detected: bool
    word_type: Optional[WakeWordType] = None
    keyword: str = ""
    confidence: float = 0.0
    engine_used: WakeWordEngine = WakeWordEngine.TEXT_MATCH
    command_args: Optional[str] = None  # Extra text after the keyword
    latency_ms: float = 0.0


# ── Keyword Patterns ─────────────────────────────────────

WAKE_PATTERNS: list[tuple[re.Pattern, WakeWordType, str]] = [
    # Deactivation (check first — more specific)
    (re.compile(r"\bnael\s+(stop|quiet|silence|shut\s*up|go\s+away)\b", re.I), WakeWordType.DEACTIVATE, "nael_stop"),
    (re.compile(r"\bnael\s+mute\b", re.I), WakeWordType.MUTE, "nael_mute"),
    (re.compile(r"\bnael\s+unmute\b", re.I), WakeWordType.UNMUTE, "nael_unmute"),
    (re.compile(r"\bnael\s+end\s*(session|surgery)?\b", re.I), WakeWordType.END, "nael_end"),

    # Acknowledge
    (re.compile(r"\b(acknowledge|ack|roger|noted|okay\s+nael)\b", re.I), WakeWordType.ACKNOWLEDGE, "acknowledge"),
    (re.compile(r"\bnael\s+acknowledge\b", re.I), WakeWordType.ACKNOWLEDGE, "nael_acknowledge"),

    # Commands (must start with "Nael")
    (re.compile(r"\bnael\s+(show|display|open)\s+(.+)", re.I), WakeWordType.COMMAND, "nael_show"),
    (re.compile(r"\bnael\s+(focus|zoom)\s+(.+)", re.I), WakeWordType.COMMAND, "nael_focus"),
    (re.compile(r"\bnael\s+(overlay|anatomy)\s+(.+)", re.I), WakeWordType.COMMAND, "nael_overlay"),
    (re.compile(r"\bnael\s+(mode)\s+(silent|reactive|proactive)\b", re.I), WakeWordType.COMMAND, "nael_mode"),
    (re.compile(r"\bnael\s+(drug|log|record)\s+(.+)", re.I), WakeWordType.COMMAND, "nael_drug"),

    # General activation (least specific — check last)
    (re.compile(r"\bnael\b", re.I), WakeWordType.ACTIVATE, "nael"),
]


class WakeWordDetector:
    """
    Detects wake words and commands in audio/text.

    In production:
      - Tier 1: Riva KWS runs continuously on the audio stream
      - Tier 2: OpenWakeWord runs on CPU as backup
      - Tier 3: Text matching on ASR output (always available)

    For Phase 1, we use text matching on the ASR transcript,
    which is what the frontend already does in useVoiceControl.ts.
    """

    def __init__(self):
        self._riva_kws_available = False
        self._openwakeword_available = False
        self._consecutive_activations = 0
        self._last_activation_time = 0.0
        self._cooldown_seconds = 2.0  # Prevent re-triggering within 2s

    async def detect_in_text(self, transcript: str) -> WakeWordResult:
        """
        Detect wake words in a text transcript (Tier 3 / always available).

        Args:
            transcript: The ASR output text to scan
        """
        start = time.monotonic()

        if not transcript or not transcript.strip():
            return WakeWordResult(detected=False)

        text = transcript.strip()

        for pattern, word_type, keyword in WAKE_PATTERNS:
            match = pattern.search(text)
            if match:
                # Cooldown check
                now = time.monotonic()
                if word_type == WakeWordType.ACTIVATE and \
                   (now - self._last_activation_time) < self._cooldown_seconds:
                    continue  # Skip — too soon after last activation

                if word_type == WakeWordType.ACTIVATE:
                    self._last_activation_time = now

                # Extract command arguments if present
                command_args = None
                if word_type == WakeWordType.COMMAND and match.lastindex and match.lastindex >= 2:
                    command_args = match.group(match.lastindex).strip()

                elapsed = (time.monotonic() - start) * 1000
                return WakeWordResult(
                    detected=True,
                    word_type=word_type,
                    keyword=keyword,
                    confidence=0.95,  # Text match is high confidence
                    engine_used=WakeWordEngine.TEXT_MATCH,
                    command_args=command_args,
                    latency_ms=elapsed,
                )

        return WakeWordResult(detected=False, latency_ms=(time.monotonic() - start) * 1000)

    async def detect_in_audio(self, audio_b64: str, codec: str = "opus") -> WakeWordResult:
        """
        Detect wake word in raw audio (Tier 1: Riva KWS, Tier 2: OpenWakeWord).

        This runs BEFORE full ASR — it's a lightweight classifier that
        only looks for "Nael" in the audio, not full transcription.
        """
        start = time.monotonic()

        # Tier 1: Riva KWS
        if self._riva_kws_available:
            result = await self._try_riva_kws(audio_b64, codec, start)
            if result and result.detected:
                return result

        # Tier 2: OpenWakeWord
        if self._openwakeword_available:
            result = await self._try_openwakeword(audio_b64, codec, start)
            if result and result.detected:
                return result

        # Tier 3: No audio-level detection available
        # Return not-detected — caller should fall back to text matching
        return WakeWordResult(
            detected=False,
            latency_ms=(time.monotonic() - start) * 1000,
        )

    async def _try_riva_kws(self, audio_b64: str, codec: str,
                             start: float) -> Optional[WakeWordResult]:
        """
        NVIDIA Riva Keyword Spotting.

        Riva KWS is a lightweight neural model that runs continuously
        and detects a configured keyword ("Nael") in the audio stream.
        Latency: ~30-50ms.
        """
        # TODO: Implement when Riva is deployed
        # import riva.client
        # auth = riva.client.Auth(uri=settings.riva_grpc_url)
        # kws = riva.client.KWSService(auth)
        # config = riva.client.StreamingRecognitionConfig(
        #     config=riva.client.RecognitionConfig(
        #         language_code="en-US",
        #         keywords=["Nael"],
        #         keyword_threshold=0.7,
        #     )
        # )
        return None

    async def _try_openwakeword(self, audio_b64: str, codec: str,
                                 start: float) -> Optional[WakeWordResult]:
        """
        OpenWakeWord — open-source wake word detection.

        Runs on CPU, ~100ms latency. Good accuracy for custom keywords.
        https://github.com/dscripka/openWakeWord
        """
        # TODO: Implement when OpenWakeWord is deployed
        # import openwakeword
        # model = openwakeword.Model(wakeword_models=["nael_v1"])
        # prediction = model.predict(audio_data)
        return None

    async def health_check(self) -> dict:
        """Check which wake word engines are available."""
        return {
            "riva_kws": self._riva_kws_available,
            "openwakeword": self._openwakeword_available,
            "text_match": True,  # Always available
        }


# Singleton
_detector: Optional[WakeWordDetector] = None


def get_wake_word_detector() -> WakeWordDetector:
    global _detector
    if _detector is None:
        _detector = WakeWordDetector()
    return _detector
