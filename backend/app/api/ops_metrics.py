"""Operational metrics & subsystem health (production gates / SLO probes)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request

from app.agents.asr_pipeline import get_asr_pipeline
from app.agents.tts_router import get_tts_router
from app.agents.wake_word import get_wake_word_detector
from app.camera.vision_orchestrator import get_vision_orchestrator
from app.config import settings
from app.nemoclaw.config_bundle import get_nemoclaw_summary
from app.nemoclaw.mcp_client import probe_mcp_health

router = APIRouter()


@router.get("/metrics/summary")
async def metrics_summary(request: Request) -> dict[str, Any]:
    """HTTP counters + coarse subsystem health for dashboards."""
    app_metrics = getattr(request.app.state, "metrics", {}) or {}
    asr_pipe = get_asr_pipeline()
    h_asr = asr_pipe.get_health()

    nemoclaw_health = []
    if settings.nemoclaw_enabled:
        nemoclaw_health = [
            await probe_mcp_health(settings.marma_mcp_url),
            await probe_mcp_health(settings.drug_mcp_url),
            await probe_mcp_health(settings.safety_mcp_url),
        ]

    return {
        "http_requests_total": int(app_metrics.get("requests", 0)),
        "ws_live_sessions_active": int(app_metrics.get("ws_live_sessions", 0)),
        "runtime": {
            "mode": settings.runtime_mode.value,
            "demo_mode": settings.demo_mode,
            "gpu_provider": settings.gpu_provider.value,
        },
        "asr": {
            "riva_available": h_asr.riva_available,
            "gemini_available": h_asr.gemini_available,
            "openrouter_available": h_asr.openrouter_available,
            "active_engine": h_asr.active_engine.value,
            "last_check": h_asr.last_check,
        },
        "tts": {
            "fish_healthy": getattr(get_tts_router(), "_fish_healthy", True),
            "piper_healthy": getattr(get_tts_router(), "_piper_healthy", True),
            "riva_tts_healthy": getattr(get_tts_router(), "_riva_tts_healthy", True),
            "riva_asr_tier_hint": h_asr.riva_available,
        },
        "wake_word": await get_wake_word_detector().health_check(),
        "vision": get_vision_orchestrator().get_health(),
        "nemoclaw": {
            "summary": get_nemoclaw_summary(),
            "mcp_health": nemoclaw_health,
        },
    }
