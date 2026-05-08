"""Conversational TTS — prefer OpenRouter `/audio/speech` when key present; else WAV fallback."""

from __future__ import annotations

import asyncio
import math
import os
import wave
from io import BytesIO

import httpx
from fastapi import FastAPI, Response

app = FastAPI(title="ShalyaMitra Fish Speech TTS")

OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_BASE = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
ALLOW_AUDIO_PLACEHOLDER = (
    str(os.environ.get("ALLOW_AUDIO_PLACEHOLDER", "false")).strip().lower() == "true"
)


def _placeholder_wav(text: str) -> bytes:
    duration = min(8.0, max(0.8, len(text) * 0.06))
    sample_rate = 24000
    nframes = int(sample_rate * duration)
    buf = BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        for i in range(nframes):
            t = i / sample_rate
            sample = int(26000 * math.sin(2 * math.pi * 320 * t))
            wf.writeframes(sample.to_bytes(2, byteorder="little", signed=True))
    return buf.getvalue()


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "fish-speech-router",
        "openrouter_configured": bool(OPENROUTER_KEY),
        "wav_fallback": ALLOW_AUDIO_PLACEHOLDER,
    }


@app.post("/v1/tts")
async def tts(body: dict):
    """Matches backend FishSpeech contract (`text`, optional `format`, `streaming`, ...)."""
    text = str(body.get("text") or "")[:12000]

    if OPENROUTER_KEY:
        try:
            async with httpx.AsyncClient(timeout=60.0) as http:
                resp = await http.post(
                    f"{OPENROUTER_BASE.rstrip('/')}/audio/speech",
                    headers={
                        "Authorization": f"Bearer {OPENROUTER_KEY}",
                        "HTTP-Referer": "https://shalyamitra.quaasx108.com",
                        "X-Title": "ShalyaMitra Fish Speech Proxy",
                    },
                    json={
                        "model": "openai/tts-1",
                        "input": text,
                        "voice": "nova",
                        "response_format": "wav",
                    },
                )
            if resp.status_code == 200:
                raw = resp.content
                if raw.startswith(b"RIFF"):
                    return Response(content=raw, media_type="audio/wav")
        except Exception:
            pass

    if ALLOW_AUDIO_PLACEHOLDER:
        wav = await asyncio.to_thread(_placeholder_wav, text)
        return Response(content=wav, media_type="audio/wav")
    return Response(
        content=b'{"detail":"Fish speech unavailable and placeholder disabled"}',
        media_type="application/json",
        status_code=503,
    )
