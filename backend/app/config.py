"""
ShalyaMitra Backend — Configuration

All secrets and tunables read from environment variables or .env file.
Uses pydantic-settings for type-safe config with defaults.
"""

from __future__ import annotations
from enum import Enum
from pydantic_settings import BaseSettings, SettingsConfigDict


class GpuProvider(str, Enum):
    nebius = "nebius"
    lightning = "lightning"
    local = "local"
    demo = "demo"


class Settings(BaseSettings):
    """Application settings — loaded from environment / .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── App ────────────────────────────────────────────────
    app_name: str = "ShalyaMitra Backend"
    app_version: str = "1.0.0"
    debug: bool = False
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:8080",
        "http://localhost:3000",
        "https://*.lightning.ai",
        "https://*.vercel.app",
        "https://shalyamitra.dev",
        "https://app.shalyamitra.dev",
    ]

    # ── Supabase (auth + DB) ──────────────────────────────
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    supabase_jwt_secret: str = ""

    # ── GPU ────────────────────────────────────────────────
    gpu_provider: GpuProvider = GpuProvider.demo
    gpu_backend_url: str = ""
    gpu_backend_token: str = ""

    # ── LiveKit ───────────────────────────────────────────
    livekit_url: str = "ws://localhost:7880"
    livekit_api_key: str = ""
    livekit_api_secret: str = ""

    # ── Redis ─────────────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"

    # ── Qdrant ────────────────────────────────────────────
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection_shalyatantra: str = "shalyatantra"
    qdrant_collection_medical: str = "medical_kb"
    qdrant_collection_drugs: str = "drug_db"

    # ── OpenRouter (fallback / Scholar / Consultant) ──────
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    scholar_model: str = "anthropic/claude-sonnet-4"
    consultant_model: str = "openai/gpt-4.1"
    chronicler_model: str = "anthropic/claude-sonnet-4"

    # ── Zero-Shot Instrument Detection ──────────────────
    # Tier 1: Grounding DINO 1.5 Pro (best accuracy)
    # Apply for token: https://deepdataspace.com
    grounding_dino_api_token: str = ""
    # Tier 2: Florence-2 (local, free, MIT licence — no key needed)
    florence2_enabled: bool = True
    florence2_model: str = "microsoft/Florence-2-large"
    # Tier 3: Gemini Flash — uses openrouter_api_key above (already set)

    # ── NVIDIA NIM API (cloud — integrate.api.nvidia.com) ─
    # Free: 1,000 calls/month. Get key: build.nvidia.com
    # OpenAI-compatible REST API — no local GPU needed.
    nvidia_api_key: str = ""
    nvidia_nim_base_url: str = "https://integrate.api.nvidia.com/v1"
    ngc_api_key: str = ""   # For pulling NGC containers on GPU server

    # Live NIM test: use real NIM API calls during demo sessions
    # Automatically enabled when NVIDIA_API_KEY is set
    nim_live_test: bool = True

    # Tier 1 — Primary reasoning (all agent LLM calls)
    nim_reasoning_model: str = "nvidia/llama-3.3-nemotron-super-49b-v1"
    # Tier 2 — Thinking/reasoning fallback (Scholar, Consultant)
    nim_thinking_model: str = "moonshotai/kimi-k2.5"
    # Tier 3 — Fast fallback (quick responses)
    nim_fast_model: str = "nvidia/nemotron-3-nano-30b-a3b"

    # NIM Vision — surgical field analysis (Cam3)
    nim_vision_model: str = "nvidia/nemotron-nano-12b-v2-vl"

    # NIM Content Safety — guardrails for clinical output
    nim_safety_model: str = "nvidia/nemotron-content-safety-reasoning-4b"

    # ── NVIDIA Riva (ASR + KWS) ──────────────────────────
    riva_grpc_url: str = "localhost:50051"

    # ── Fish Speech TTS ──────────────────────────────────
    fish_speech_url: str = "http://localhost:8080"

    # ── Piper TTS (Critical Alert Path) ──────────────────
    piper_url: str = "http://localhost:8090"

    # ── MinIO (file storage) ─────────────────────────────
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "shalyamitra"
    minio_secure: bool = False

    # ── Session Defaults ─────────────────────────────────
    max_session_hours: int = 8
    default_mode: str = "reactive"
    alert_audio_dir: str = "/app/alerts/pregenerated"


settings = Settings()
