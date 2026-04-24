"""
NVIDIA Riva — HTTP helpers for TTS, NMT, and diarization metadata.

Riva primarily uses gRPC on :50051; many deployments also expose REST on
:8000/:8001. Paths vary by Riva version — this module tries several common
shapes and reads optional diarization fields from ASR JSON.
"""

from __future__ import annotations

import base64
import re
from typing import Any, Optional

import httpx

from app.config import settings


def _riva_base() -> str:
    return settings.riva_http_base.rstrip("/")


def map_speaker_label(raw: Optional[str | int]) -> str:
    """Map Riva diarization id to a coarse OR role label for the UI."""
    if raw is None:
        return "unknown"
    s = str(raw).lower()
    if s in ("0", "speaker_0", "spk_0", "a"):
        return "surgeon"
    if s in ("1", "speaker_1", "spk_1", "b"):
        return "anaesthetist"
    if s in ("2", "speaker_2", "spk_2", "c"):
        return "staff"
    return f"speaker_{raw}"


def extract_speaker_from_asr_json(data: dict[str, Any]) -> Optional[str]:
    """
    Parse optional diarization / speaker fields from Riva (or compatible) ASR JSON.
    Supports a few common response shapes.
    """
    if not data:
        return None
    # Whole-utterance speaker
    for key in ("speaker", "speaker_label", "primary_speaker", "spk_id"):
        if key in data and data[key] is not None:
            return map_speaker_label(data[key])
    # Segments with speaker per segment (use first segment)
    segs = data.get("segments") or data.get("results", [])
    if isinstance(segs, list) and segs:
        sp = segs[0].get("speaker") or segs[0].get("speaker_tag")
        if sp is not None:
            return map_speaker_label(sp)
    # Word-level tags
    words = data.get("words") or data.get("alternatives", [{}])[0].get("words", [])
    if isinstance(words, list) and words:
        sp = words[0].get("speaker_tag") or words[0].get("speaker")
        if sp is not None:
            return map_speaker_label(sp)
    return None


async def riva_synthesize_tts(text: str, voice: Optional[str] = None) -> Optional[bytes]:
    """
    Synthesize speech via Riva HTTP. Tries several URL patterns used across Riva releases.
    Returns raw audio bytes (wav) or None.
    """
    if not settings.riva_tts_enable or not text.strip():
        return None
    voice_name = voice or settings.riva_tts_voice
    base = _riva_base()
    payloads = [
        {"text": text, "voice_name": voice_name},
        {"text": text, "voice": voice_name},
        {"input": text, "voice": voice_name},
    ]
    paths = (
        "/v1/tts/synthesize",
        "/tts/synthesize",
        "/v1/speech:synthesize",
        "/tts",
    )
    try:
        async with httpx.AsyncClient(timeout=15.0) as http:
            for path in paths:
                for body in payloads:
                    try:
                        r = await http.post(f"{base}{path}", json=body)
                        if r.status_code != 200:
                            continue
                        ct = (r.headers.get("content-type") or "").lower()
                        if "json" in ct:
                            d = r.json()
                            b64 = d.get("audio") or d.get("audio_content")
                            if isinstance(b64, str):
                                return base64.b64decode(b64)
                            aud = d.get("audioData")
                            if isinstance(aud, (bytes, bytearray)):
                                return bytes(aud)
                        # Raw audio
                        if r.content[:4] in (b"RIFF", b"\x1a\x45", b"OggS") or "audio" in ct:
                            return r.content
                    except Exception:
                        continue
    except Exception:
        return None
    return None


async def riva_translate_nmt(
    text: str,
    source_lang: Optional[str] = None,
    target_lang: Optional[str] = None,
) -> Optional[str]:
    """Neural machine translation via Riva NMT HTTP (if enabled and exposed)."""
    if not settings.riva_nmt_enable or not text.strip():
        return None
    src = source_lang or settings.riva_nmt_default_source
    tgt = target_lang or settings.riva_nmt_default_target
    base = _riva_base()
    body = {
        "text": text,
        "source_language": src,
        "target_language": tgt,
    }
    paths = ("/nmt/translate", "/v1/nmt:translate", "/v1/translate", "/nmt")
    try:
        async with httpx.AsyncClient(timeout=15.0) as http:
            for path in paths:
                try:
                    r = await http.post(f"{base}{path}", json=body)
                    if r.status_code == 200:
                        d = r.json()
                        out = d.get("translated_text") or d.get("translation") or d.get("text")
                        if isinstance(out, str) and out.strip():
                            return out
                except Exception:
                    continue
    except Exception:
        return None
    return None


def with_acoustic_hint(headers: dict[str, str]) -> dict[str, str]:
    """Optional custom acoustic model (fine-tune) header for Riva ASR requests."""
    h = dict(headers)
    if settings.riva_acoustic_model:
        h["X-Riva-Model"] = settings.riva_acoustic_model
    return h
