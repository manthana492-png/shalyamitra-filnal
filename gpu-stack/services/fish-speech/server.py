"""Fish Speech 1.5 placeholder — use official Fish Speech + GPU for production TTS."""

from fastapi import FastAPI

app = FastAPI(title="Fish Speech (stub)")


@app.get("/health")
def health():
    return {"status": "ok", "service": "fish-speech-stub"}


@app.post("/v1/tts")
def tts():
    return {"ok": True, "note": "Stub — configure real Fish Speech for audio output."}
