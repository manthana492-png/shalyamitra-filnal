"""Piper-compatible critical-alert TTS — ONNX Piper CLI when available, else WAV fallback."""

from __future__ import annotations

import asyncio
import math
import os
import subprocess
import wave
from io import BytesIO

from fastapi import FastAPI, Response

MODEL_PATH = os.environ.get("PIPER_MODEL_PATH", "/models/en_US-lessac-medium.onnx")
ALLOW_AUDIO_PLACEHOLDER = (
    str(os.environ.get("ALLOW_AUDIO_PLACEHOLDER", "false")).strip().lower() == "true"
)

app = FastAPI(title="ShalyaMitra Piper TTS")


def _placeholder_wav(text: str) -> bytes:
    """Deterministic short tone so CI / offline stacks still return audio bytes."""
    duration = min(6.0, max(0.6, len(text) * 0.05))
    sample_rate = 22050
    nframes = int(sample_rate * duration)
    buf = BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        for i in range(nframes):
            # soft rising tone (easy to recognise as synthetic fallback)
            t = i / sample_rate
            sample = int(32000 * math.sin(2 * math.pi * (440 + 120 * t) * t))
            wf.writeframes(sample.to_bytes(2, byteorder="little", signed=True))
    return buf.getvalue()


def _run_piper_cli(text: str) -> bytes | None:
    try:
        proc = subprocess.run(
            [
                "piper",
                "--model",
                MODEL_PATH,
                "--output_file",
                "-",
            ],
            input=text.encode("utf-8"),
            capture_output=True,
            timeout=45,
            check=False,
        )
        out = proc.stdout or b""
        if proc.returncode == 0 and out.startswith(b"RIFF"):
            return out
    except Exception:
        pass
    return None


@app.get("/health")
def health():
    ok_cli = False
    try:
        subprocess.run(["piper", "--help"], capture_output=True, timeout=2, check=False)
        ok_cli = True
    except Exception:
        ok_cli = False
    return {
        "status": "ok",
        "service": "piper-tts",
        "model_path": MODEL_PATH,
        "piper_cli": ok_cli,
        "wav_fallback": ALLOW_AUDIO_PLACEHOLDER,
    }


@app.post("/api/tts")
async def synthesize(body: dict):
    """Contract matches backend `tts_router.TTSRouter._critical_path`."""
    text = str(body.get("text") or "")[:8000]

    def _work() -> bytes | None:
        wav = _run_piper_cli(text)
        if wav:
            return wav
        if ALLOW_AUDIO_PLACEHOLDER:
            return _placeholder_wav(text)
        return None

    audio = await asyncio.to_thread(_work)
    if not audio:
        return Response(
            content=b'{"detail":"Piper synthesis unavailable and placeholder disabled"}',
            media_type="application/json",
            status_code=503,
        )
    return Response(content=audio, media_type="audio/wav")
