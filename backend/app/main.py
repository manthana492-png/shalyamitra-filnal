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

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api import sessions, preop, postop, profiles, admin, voice, camera, marma, safety
from app.ws.realtime import router as ws_router


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
    stats = get_marma_stats()
    _ = get_phi_middleware()        # warm up PHI engine
    __ = get_guardrails_engine()    # warm up guardrails
    pr = get_privacy_router()       # warm up privacy router

    print(f"[START] {settings.app_name} v{settings.app_version} starting")
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
    print(f"   MCP Servers  : marma(3001) drug(3002) safety(3003)")
    yield
    # ── Shutdown ──────────────────────────────────────────
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

# ── WebSocket Realtime ────────────────────────────────────
app.include_router(ws_router)


# ── Health Check ──────────────────────────────────────────
@app.get("/healthz", tags=["Health"])
async def healthz():
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": settings.app_version,
        "gpu_provider": settings.gpu_provider.value,
    }


@app.get("/", tags=["Health"])
async def root():
    return {
        "service": "ShalyaMitra Backend",
        "version": settings.app_version,
        "docs": "/docs",
    }
