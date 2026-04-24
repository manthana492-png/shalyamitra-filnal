"""
ShalyaMitra — Voice Settings API

Endpoints for the surgeon to:
  1. List available voice profiles
  2. Select preferred Nael voice
  3. Upload custom voice sample
  4. Check ASR/TTS engine health
  5. Test a voice profile (preview)
"""

from __future__ import annotations

import base64
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel

from app.auth.jwt import get_current_user, AuthUser
from app.agents.voice_profiles import get_voice_manager
from app.agents.asr_pipeline import get_asr_pipeline
from app.agents.tts_router import get_tts_router
from app.config import settings
from app.speech.riva_client import riva_translate_nmt


router = APIRouter()


class VoicePreferenceUpdate(BaseModel):
    voice_id: str


class VoiceTestRequest(BaseModel):
    voice_id: Optional[str] = None
    text: str = "Good morning, Doctor. Pre-operative analysis loaded. I'm here when you need me."


class NmtRequest(BaseModel):
    """Riva NMT: translate theatre speech or transcripts (e.g. en → hi)."""
    text: str
    source_lang: str = "en"
    target_lang: str = "hi"


@router.get("/voices")
async def list_voices(user: AuthUser = Depends(get_current_user)):
    """
    List all available voice profiles.
    Returns selectable voices for the settings UI.
    """
    mgr = get_voice_manager()
    return {
        "voices": mgr.get_selectable_voices(),
        "current_preference": mgr.surgeon_preference,
    }


@router.post("/voices/preference")
async def set_voice_preference(
    body: VoicePreferenceUpdate,
    user: AuthUser = Depends(get_current_user),
):
    """Set the surgeon's preferred conversational Nael voice."""
    mgr = get_voice_manager()
    available = [v["id"] for v in mgr.get_selectable_voices()]
    if body.voice_id not in available:
        raise HTTPException(status_code=400, detail=f"Voice '{body.voice_id}' not available or not selectable")
    mgr.set_surgeon_preference(body.voice_id)
    # TODO: Persist to Supabase profiles.voice_preference
    return {"status": "updated", "voice_id": body.voice_id}


@router.post("/voices/custom")
async def upload_custom_voice(
    file: UploadFile = File(...),
    user: AuthUser = Depends(get_current_user),
):
    """
    Upload a custom voice sample (10-30s WAV/MP3).
    Fish Speech uses this as a reference for voice cloning.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    # Validate file type
    allowed = {"audio/wav", "audio/mpeg", "audio/mp3", "audio/wave", "audio/x-wav"}
    if file.content_type and file.content_type not in allowed:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {file.content_type}. Use WAV or MP3.")

    # Read and validate size (max 5MB)
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Maximum 5MB.")
    if len(content) < 10000:
        raise HTTPException(status_code=400, detail="File too small. Need at least 10 seconds of audio.")

    # Create custom voice profile
    voice_id = f"custom_{str(user.sub)[:8]}_{uuid4().hex[:6]}"
    audio_b64 = base64.b64encode(content).decode("utf-8")

    mgr = get_voice_manager()
    mgr.add_custom_voice(
        voice_id=voice_id,
        name=f"Custom Voice ({file.filename})",
        description=f"Uploaded by surgeon. File: {file.filename}",
        reference_audio_b64=audio_b64,
        user_id=str(user.sub),
    )

    # Auto-select the newly uploaded voice
    mgr.set_surgeon_preference(voice_id)

    # TODO: Persist reference audio to MinIO
    return {
        "status": "uploaded",
        "voice_id": voice_id,
        "name": f"Custom Voice ({file.filename})",
    }


@router.post("/voices/test")
async def test_voice(
    body: VoiceTestRequest,
    user: AuthUser = Depends(get_current_user),
):
    """
    Preview a voice by synthesizing a test phrase.
    Returns base64-encoded audio the frontend can play.
    """
    tts = get_tts_router()

    # If voice_id specified, temporarily use it
    mgr = get_voice_manager()
    original_pref = mgr.surgeon_preference
    if body.voice_id:
        mgr.set_surgeon_preference(body.voice_id)

    result = await tts.synthesize(body.text, pillar="nael")

    # Restore original preference
    mgr.set_surgeon_preference(original_pref)

    return {
        "audio_b64": result.audio_b64,
        "mime_type": result.mime_type,
        "engine_used": result.engine_used.value,
        "voice_id": result.voice_id,
        "latency_ms": round(result.latency_ms, 1),
        "is_fallback": result.is_fallback,
    }


@router.post("/translate")
async def translate_text(
    body: NmtRequest,
    user: AuthUser = Depends(get_current_user),
):
    """
    Neural machine translation via NVIDIA Riva NMT (when enabled and HTTP exposed).
    """
    if not settings.riva_nmt_enable:
        raise HTTPException(status_code=400, detail="NMT disabled in configuration")
    out = await riva_translate_nmt(
        body.text, body.source_lang, body.target_lang
    )
    if not out:
        raise HTTPException(
            status_code=502,
            detail="NMT unavailable — check Riva NMT is enabled and riva_http_base is correct",
        )
    return {
        "translated_text": out,
        "source_lang": body.source_lang,
        "target_lang": body.target_lang,
    }


@router.get("/health")
async def audio_health(user: AuthUser = Depends(get_current_user)):
    """
    Check the health of all audio engines (ASR + TTS).
    Shows which tiers are active and which are on fallback.
    """
    asr = get_asr_pipeline()
    asr_health = asr.get_health()

    tts = get_tts_router()

    return {
        "asr": {
            "active_engine": asr_health.active_engine.value,
            "riva_available": asr_health.riva_available,
            "gemini_available": asr_health.gemini_available,
            "openrouter_available": asr_health.openrouter_available,
            "fallback_chain": ["riva", "gemini_flash", "whisper_openrouter", "browser"],
        },
        "tts": {
            "riva_tts_enabled": settings.riva_tts_enable,
            "riva_tts_available": getattr(tts, "_riva_tts_healthy", True),
            "fish_speech_available": tts._fish_healthy,
            "piper_available": tts._piper_healthy,
            "openrouter_available": bool(settings.openrouter_api_key),
            "browser_fallback": True,  # Always available
            "fallback_chain": [
                "piper (critical)",
                "riva_tts (info)",
                "fish_speech",
                "gemini/openrouter",
                "browser",
            ],
        },
        "nmt": {
            "riva_nmt_enabled": settings.riva_nmt_enable,
        },
        "ingest": {
            "video_ingest_mode": settings.video_ingest_mode,
        },
        "wake_word": {
            "riva_kws": False,       # Not yet deployed
            "openwakeword": False,   # Not yet deployed
            "text_match": True,      # Always available
        },
    }
