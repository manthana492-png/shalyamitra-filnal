"""Critical-alert TTS placeholder. Swap for rhasspy/piper + ONNX models in production."""

from fastapi import FastAPI

app = FastAPI(title="Piper (stub)")


@app.get("/health")
def health():
    return {"status": "ok", "service": "piper-stub"}


@app.post("/synthesize")
def synthesize():
    return {"audio": "stub", "format": "wav"}
