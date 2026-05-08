"""
ShalyaMitra Backend — FastAPI Application Entry Point

Central API server that:
  1. Serves REST endpoints for session CRUD, pre-op, post-op, profiles, admin
  2. Serves the WebSocket realtime endpoint (replaces Supabase edge functions)
  3. Manages GPU session lifecycle
  4. Routes events between the GPU stack and the frontend
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api import sessions, preop, postop, profiles, admin, voice, camera, marma, safety
from app.api import internal_holoscan, internal_camera, ops_metrics
from app.ws.realtime import router as ws_router
from app.ws.rtc_signaling import router as rtc_router


async def _display_fanout(event) -> None:
    """Route orchestrator display_* events → per-session WebSocket fan-out."""
    from app.ws.display_wire import enrich_display_for_wire
    from app.session.lifecycle import get_session_manager

    ev = await enrich_display_for_wire(event)
    sid = ev.session_id
    if sid:
        await get_session_manager()._broadcast_event(sid, ev)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle."""
    # ── Startup ───────────────────────────────────────────
    from app.agents.orchestrator import get_orchestrator
    from app.knowledge.marma_db import get_marma_stats
    from app.safety.phi_redaction import get_phi_middleware
    from app.safety.clinical_guardrails import get_guardrails_engine
    from app.safety.privacy_router import get_privacy_router

    orch = get_orchestrator()
    orch.add_display_callback(_display_fanout)
    stats = get_marma_stats()
    _ = get_phi_middleware(), get_guardrails_engine(), get_privacy_router()

    from app.nemoclaw.config_bundle import get_nemoclaw_summary

    nc = get_nemoclaw_summary()

    print(f"[START] {settings.app_name} v{settings.app_version} starting")
    print(f"   Runtime      : {settings.runtime_mode.value} (demo={'on' if settings.demo_mode else 'off'})")
    print(f"   GPU provider : {settings.gpu_provider.value}")
    print(f"   Debug mode   : {settings.debug}")
    print(f"   Agents       : {len(orch.agents)} pillars (ShalyaBus)")
    print(f"   Marma DB     : {stats['total_points']} points ({stats['total_entries']} entries)")
    print(f"   PHI Redaction: active (17 Indian ID patterns)")
    print(f"   Guardrails   : active (LLM={'enabled' if settings.openrouter_api_key else 'disabled'})")
    nim_status = "NIM API configured" if settings.nvidia_api_key else "no NVIDIA_API_KEY — set at build.nvidia.com"
    print(f"   NIM API      : {nim_status}")
    print(f"   NIM Models   : {settings.nim_reasoning_model} (primary), {settings.nim_thinking_model} (thinking)")
    print(f"   NIM Vision   : {settings.nim_vision_model}")
    print(
        f"   Video ingest : {settings.video_ingest_mode} "
        f"(holoscan bridge: {settings.holoscan_base_url or 'not set'})"
    )
    print(
        f"   Riva stack   : HTTP {settings.riva_http_base} | "
        f"TTS={'on' if settings.riva_tts_enable else 'off'} | "
        f"NMT={'on' if settings.riva_nmt_enable else 'off'}"
    )
    print(
        f"   NemoClaw      : {'on' if settings.nemoclaw_enabled else 'off'} "
        f"| bundle={nc.get('sandbox_count', 0)} sandboxes | "
        f"policy_yaml=v{nc.get('openshell_policy_version') or '?'}"
    )
    print(
        f"   NemoClaw MCP  : marma {settings.marma_mcp_url} | "
        f"drug {settings.drug_mcp_url} | safety {settings.safety_mcp_url}"
    )
    yield
    # ── Shutdown ──────────────────────────────────────────
    orch.remove_display_callback(_display_fanout)
    print(f"[STOP] {settings.app_name} shutting down")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "ShalyaMitra surgical intelligence backend. "
        "Provides REST APIs for session management and a WebSocket "
        "realtime endpoint connecting the Theatre Display to the GPU stack."
    ),
    lifespan=lifespan,
)

app.state.metrics = {"requests": 0, "ws_live_sessions": 0}


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    response = await call_next(request)
    m = getattr(request.app.state, "metrics", None)
    if isinstance(m, dict):
        m["requests"] = int(m.get("requests", 0)) + 1
    return response


# ── CORS ──────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── REST API Routers ──────────────────────────────────────
app.include_router(sessions.router, prefix="/api/sessions", tags=["Sessions"])
app.include_router(preop.router, prefix="/api/preop", tags=["Pre-Op"])
app.include_router(postop.router, prefix="/api/postop", tags=["Post-Op"])
app.include_router(profiles.router, prefix="/api/profiles", tags=["Profiles"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(voice.router, prefix="/api/voice", tags=["Voice"])
app.include_router(camera.router, prefix="/api/camera", tags=["Camera"])
app.include_router(marma.router, prefix="/api/marma", tags=["Marma Knowledge"])
app.include_router(safety.router, prefix="/api/safety", tags=["Safety & Compliance"])
app.include_router(ops_metrics.router, prefix="/api/ops", tags=["Operations"])
app.include_router(
    internal_holoscan.router,
    prefix="/api/internal",
    tags=["Internal — Holoscan"],
)
app.include_router(
    internal_camera.router,
    prefix="/api/internal",
    tags=["Internal — Camera"],
)

# ── WebSocket Realtime ────────────────────────────────────
app.include_router(ws_router)
app.include_router(rtc_router)


# ── Health Check ──────────────────────────────────────────
@app.get("/healthz", tags=["Health"])
async def healthz():
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": settings.app_version,
        "gpu_provider": settings.gpu_provider.value,
        "holoscan_bridge": settings.holoscan_base_url or None,
        "video_ingest_mode": settings.video_ingest_mode,
        "runtime_mode": settings.runtime_mode.value,
        "demo_mode": settings.demo_mode,
    }


@app.get("/", tags=["Health"])
async def root():
    return {
        "service": "ShalyaMitra Backend",
        "version": settings.app_version,
        "docs": "/docs",
    }
