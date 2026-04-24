"""
ShalyaMitra — ASR Pipeline (Speech-to-Text)

3-tier fallback ASR architecture:

  Tier 1: NVIDIA Riva (self-hosted on GPU)
    - Streaming gRPC, ~100-200ms latency
    - Works offline in hospital networks
    - Built-in wake word detection ("Nael")
    - PHI-safe: audio never leaves the GPU box

  Tier 2: Gemini Flash / OpenRouter (cloud API)
    - ~300-600ms latency (network round-trip)
    - Good medical vocabulary out-of-box
    - Requires internet connection
    - Free tier available

  Tier 3: Browser Web Speech API (client-side)
    - ~200-500ms latency (varies by browser)
    - Already implemented in frontend's useVoiceControl.ts
    - No server dependency
    - Worst accuracy for medical terms

The ASR pipeline automatically falls back through tiers on failure.
"""

from __future__ import annotations

import asyncio
import base64
import time
from dataclasses import dataclass
from enum import Enum
from typing import AsyncIterator, Optional

import httpx

from app.config import settings
from app.speech.riva_client import extract_speaker_from_asr_json, with_acoustic_hint


class ASREngine(str, Enum):
    RIVA = "riva"
    GEMINI = "gemini"
    OPENROUTER = "openrouter"
    BROWSER = "browser"


class ASRStatus(str, Enum):
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    ERROR = "error"


@dataclass
class ASRResult:
    """Result from speech recognition."""
    text: str
    confidence: float
    engine_used: ASREngine
    is_final: bool              # True = final transcript, False = interim
    is_fallback: bool
    latency_ms: float
    language: str = "en-IN"
    speaker: Optional[str] = None  # Identified speaker (surgeon/anaesthetist/nurse)


@dataclass
class ASRHealth:
    """Health status of all ASR engines."""
    riva_available: bool
    gemini_available: bool
    openrouter_available: bool
    active_engine: ASREngine
    last_check: float


class ASRPipeline:
    """
    Speech-to-text pipeline with automatic failover.

    Usage:
        pipeline = get_asr_pipeline()
        result = await pipeline.transcribe(audio_b64, codec="opus")

    For streaming (real-time during surgery):
        async for result in pipeline.stream_transcribe(audio_chunks):
            handle_transcript(result)
    """

    def __init__(self):
        self._http: Optional[httpx.AsyncClient] = None
        self._riva_healthy = True
        self._gemini_healthy = True
        self._openrouter_healthy = True
        self._riva_client = None  # gRPC stub (initialized when Riva is available)
        self._active_engine = ASREngine.RIVA

    async def _get_http(self) -> httpx.AsyncClient:
        if self._http is None or self._http.is_closed:
            self._http = httpx.AsyncClient(timeout=10.0)
        return self._http

    # ══════════════════════════════════════════════════════
    # Main transcribe API
    # ══════════════════════════════════════════════════════

    async def transcribe(
        self,
        audio_b64: str,
        codec: str = "opus",
        language: str = "en-IN",
    ) -> ASRResult:
        """
        Transcribe a single audio chunk with automatic fallback.

        Args:
            audio_b64: Base64-encoded audio data
            codec: Audio codec ("opus", "pcm16", "wav")
            language: Language code
        """
        start = time.monotonic()

        # Tier 1: NVIDIA Riva
        if self._riva_healthy:
            result = await self._try_riva(audio_b64, codec, language, start)
            if result:
                self._active_engine = ASREngine.RIVA
                return result

        # Tier 2: Gemini Flash (free tier via OpenRouter)
        if self._gemini_healthy:
            result = await self._try_gemini(audio_b64, codec, language, start)
            if result:
                self._active_engine = ASREngine.GEMINI
                return result

        # Tier 3: OpenRouter other models
        if self._openrouter_healthy:
            result = await self._try_openrouter(audio_b64, codec, language, start)
            if result:
                self._active_engine = ASREngine.OPENROUTER
                return result

        # All tiers failed — return empty result
        # Frontend will use its own browser SpeechRecognition
        elapsed = (time.monotonic() - start) * 1000
        self._active_engine = ASREngine.BROWSER
        return ASRResult(
            text="",
            confidence=0.0,
            engine_used=ASREngine.BROWSER,
            is_final=True,
            is_fallback=True,
            latency_ms=elapsed,
        )

    # ══════════════════════════════════════════════════════
    # Engine Implementations
    # ══════════════════════════════════════════════════════

    async def _try_riva(self, audio_b64: str, codec: str,
                         language: str, start: float) -> Optional[ASRResult]:
        """
        NVIDIA Riva ASR via gRPC.

        Riva runs as a container on the GPU stack. We connect via
        the gRPC endpoint at settings.riva_grpc_url.

        In production, this uses the riva.client Python package:
            import riva.client
            auth = riva.client.Auth(uri=settings.riva_grpc_url)
            asr = riva.client.ASRService(auth)
        """
        try:
            # Phase 1: HTTP wrapper endpoint (Riva has a REST API too)
            http = await self._get_http()
            audio_bytes = base64.b64decode(audio_b64)

            # Riva batch recognition over HTTP (port from settings.riva_http_base)
            asr_url = f"{settings.riva_http_base.rstrip('/')}/asr/recognize"
            resp = await http.post(
                asr_url,
                content=audio_bytes,
                headers=with_acoustic_hint({
                    "Content-Type": f"audio/{codec}",
                    "Accept": "application/json",
                }),
                timeout=3.0,
            )

            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list) and data:
                    data = data[0]
                if not isinstance(data, dict):
                    data = {}
                transcript = data.get("text", "") or data.get("transcript", "")
                confidence = data.get("confidence", 0.9)
                speaker = extract_speaker_from_asr_json(data)
                elapsed = (time.monotonic() - start) * 1000
                return ASRResult(
                    text=transcript,
                    confidence=confidence,
                    engine_used=ASREngine.RIVA,
                    is_final=True,
                    is_fallback=False,
                    latency_ms=elapsed,
                    language=language,
                    speaker=speaker,
                )
        except Exception:
            self._riva_healthy = False
            asyncio.get_event_loop().call_later(30, self._reset_riva_health)

        return None

    async def _try_gemini(self, audio_b64: str, codec: str,
                           language: str, start: float) -> Optional[ASRResult]:
        """
        Google Gemini 2.0 Flash via OpenRouter — audio-to-text.

        Uses the multimodal API to send audio and get text transcription.
        Free tier on OpenRouter allows ~50 req/day.
        """
        if not settings.openrouter_api_key:
            return None

        try:
            http = await self._get_http()

            # Determine MIME type
            mime_map = {"opus": "audio/opus", "pcm16": "audio/pcm", "wav": "audio/wav"}
            mime = mime_map.get(codec, "audio/wav")

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
                                "You are a surgical speech transcription system. "
                                "Transcribe the audio exactly as spoken. "
                                "The speakers are in a surgical operating theatre. "
                                "Medical terminology should be transcribed accurately. "
                                "Output ONLY the transcription, no commentary."
                            ),
                        },
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "input_audio",
                                    "input_audio": {
                                        "data": audio_b64,
                                        "format": codec if codec in ("wav", "mp3") else "wav",
                                    },
                                },
                                {
                                    "type": "text",
                                    "text": "Transcribe this surgical audio exactly.",
                                },
                            ],
                        },
                    ],
                },
                timeout=6.0,
            )

            if resp.status_code == 200:
                data = resp.json()
                choices = data.get("choices", [])
                if choices:
                    text = choices[0].get("message", {}).get("content", "").strip()
                    if text:
                        elapsed = (time.monotonic() - start) * 1000
                        return ASRResult(
                            text=text,
                            confidence=0.85,
                            engine_used=ASREngine.GEMINI,
                            is_final=True,
                            is_fallback=True,
                            latency_ms=elapsed,
                            language=language,
                        )
        except Exception:
            self._gemini_healthy = False
            asyncio.get_event_loop().call_later(60, self._reset_gemini_health)

        return None

    async def _try_openrouter(self, audio_b64: str, codec: str,
                               language: str, start: float) -> Optional[ASRResult]:
        """
        Fallback ASR via other OpenRouter audio models.

        Tries Whisper-compatible models available on OpenRouter.
        """
        if not settings.openrouter_api_key:
            return None

        try:
            http = await self._get_http()
            audio_bytes = base64.b64decode(audio_b64)

            # Try OpenAI Whisper via OpenRouter
            resp = await http.post(
                f"{settings.openrouter_base_url}/audio/transcriptions",
                headers={
                    "Authorization": f"Bearer {settings.openrouter_api_key}",
                    "HTTP-Referer": "https://shalyamitra.dev",
                    "X-Title": "ShalyaMitra Surgical AI",
                },
                files={"file": ("audio.wav", audio_bytes, "audio/wav")},
                data={
                    "model": "openai/whisper-1",
                    "language": language[:2],  # "en"
                    "prompt": "Surgical operating theatre. Medical terminology.",
                },
                timeout=8.0,
            )

            if resp.status_code == 200:
                data = resp.json()
                text = data.get("text", "").strip()
                if text:
                    elapsed = (time.monotonic() - start) * 1000
                    return ASRResult(
                        text=text,
                        confidence=0.80,
                        engine_used=ASREngine.OPENROUTER,
                        is_final=True,
                        is_fallback=True,
                        latency_ms=elapsed,
                        language=language,
                    )
        except Exception:
            self._openrouter_healthy = False
            asyncio.get_event_loop().call_later(60, self._reset_openrouter_health)

        return None

    # ══════════════════════════════════════════════════════
    # Health Management
    # ══════════════════════════════════════════════════════

    def _reset_riva_health(self):
        self._riva_healthy = True

    def _reset_gemini_health(self):
        self._gemini_healthy = True

    def _reset_openrouter_health(self):
        self._openrouter_healthy = True

    def get_health(self) -> ASRHealth:
        return ASRHealth(
            riva_available=self._riva_healthy,
            gemini_available=self._gemini_healthy,
            openrouter_available=self._openrouter_healthy,
            active_engine=self._active_engine,
            last_check=time.time(),
        )

    async def check_all_engines(self) -> ASRHealth:
        """Actively probe all engines and update health status."""
        # Riva health check
        try:
            http = await self._get_http()
            health = f"{settings.riva_http_base.rstrip('/')}/health"
            resp = await http.get(health, timeout=2.0)
            self._riva_healthy = resp.status_code == 200
        except Exception:
            self._riva_healthy = False

        # Gemini/OpenRouter — just check if key is configured
        self._gemini_healthy = bool(settings.openrouter_api_key)
        self._openrouter_healthy = bool(settings.openrouter_api_key)

        return self.get_health()

    async def close(self):
        if self._http and not self._http.is_closed:
            await self._http.aclose()


# Singleton
_pipeline: Optional[ASRPipeline] = None


def get_asr_pipeline() -> ASRPipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = ASRPipeline()
    return _pipeline
