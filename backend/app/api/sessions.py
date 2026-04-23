"""
ShalyaMitra — Session Management API

CRUD operations for surgery sessions. The frontend's Dashboard, Sessions,
NewSession, and SessionConsole pages all talk to these endpoints.

NOTE: In Phase 1, the frontend still uses Supabase directly for session
CRUD. These endpoints exist so the backend can also manage sessions
(e.g. GPU orchestrator needs to read session data). In Phase 2, the
frontend will migrate to these endpoints.
"""

from __future__ import annotations
from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from app.auth.jwt import get_current_user, AuthUser
from app.models.schemas import (
    SessionCreate, SessionRead, SessionUpdate, SessionStatus,
)
from app.config import settings

router = APIRouter()

# In-memory store for dev — replaced by Supabase/PostgreSQL queries in prod
_sessions: dict[str, dict] = {}


@router.post("/", response_model=dict, status_code=201)
async def create_session(
    body: SessionCreate,
    user: AuthUser = Depends(get_current_user),
):
    """Create a new surgery session."""
    from uuid import uuid4
    from datetime import datetime, timezone

    session_id = str(uuid4())
    now = datetime.now(timezone.utc).isoformat()

    session = {
        "id": session_id,
        "created_by": str(user.sub),
        **body.model_dump(),
        "status": "scheduled",
        "current_mode": "reactive",
        "started_at": None,
        "ended_at": None,
        "created_at": now,
        "updated_at": now,
    }
    _sessions[session_id] = session
    return session


@router.get("/{session_id}")
async def get_session(
    session_id: str,
    user: AuthUser = Depends(get_current_user),
):
    """Get a surgery session by ID."""
    session = _sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.patch("/{session_id}")
async def update_session(
    session_id: str,
    body: SessionUpdate,
    user: AuthUser = Depends(get_current_user),
):
    """Update session status, mode, timestamps."""
    session = _sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    updates = body.model_dump(exclude_none=True)
    for key, value in updates.items():
        if isinstance(value, SessionStatus):
            session[key] = value.value
        else:
            session[key] = str(value) if hasattr(value, "isoformat") else value

    from datetime import datetime, timezone
    session["updated_at"] = datetime.now(timezone.utc).isoformat()
    return session


@router.get("/")
async def list_sessions(
    user: AuthUser = Depends(get_current_user),
    status: Optional[str] = None,
):
    """List sessions for the current user."""
    user_id = str(user.sub)
    results = [
        s for s in _sessions.values()
        if s["created_by"] == user_id
    ]
    if status:
        results = [s for s in results if s["status"] == status]
    return results


# ── Session Lifecycle ─────────────────────────────────────

@router.post("/{session_id}/start")
async def start_session(
    session_id: str,
    user: AuthUser = Depends(get_current_user),
):
    """
    Start a surgery session — initializes all pipelines.

    Phase flow:
      1. Creates session in lifecycle manager
      2. Starts pre-op (Scholar + Oracle)
      3. Starts intra-op (Vision + Audio + all 11 agents)
    """
    from app.session.lifecycle import get_session_manager

    session = _sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    mgr = get_session_manager()

    # Create in lifecycle
    await mgr.create_session(
        session_id=session_id,
        procedure=session.get("procedure_name", ""),
        patient={
            "name": session.get("patient_name", ""),
            "age": session.get("patient_age", 0),
            "weight_kg": session.get("patient_weight_kg", 70),
            "bmi": session.get("patient_bmi", 25),
            "asa": session.get("asa_grade", 2),
            "comorbidities": session.get("comorbidities", ""),
        },
        surgeon=str(user.sub),
    )

    # Run pre-op then intra-op
    await mgr.start_preop(session_id)
    result = await mgr.start_intraop(session_id)

    # Update session status
    from datetime import datetime, timezone
    session["status"] = "active"
    session["started_at"] = datetime.now(timezone.utc).isoformat()
    session["updated_at"] = datetime.now(timezone.utc).isoformat()

    return {
        "status": "active",
        "session_id": session_id,
        **result,
    }


@router.post("/{session_id}/end")
async def end_session(
    session_id: str,
    user: AuthUser = Depends(get_current_user),
):
    """
    End a surgery session — generates post-op report.
    Stops vision/audio pipelines and triggers Chronicler.
    """
    from app.session.lifecycle import get_session_manager

    session = _sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    mgr = get_session_manager()
    result = await mgr.end_surgery(session_id)

    from datetime import datetime, timezone
    session["status"] = "completed"
    session["ended_at"] = datetime.now(timezone.utc).isoformat()
    session["updated_at"] = datetime.now(timezone.utc).isoformat()

    return result


@router.get("/{session_id}/health")
async def session_health(
    session_id: str,
    user: AuthUser = Depends(get_current_user),
):
    """Get live health status of an active session."""
    from app.session.lifecycle import get_session_manager
    from app.camera.vision_orchestrator import get_vision_orchestrator

    mgr = get_session_manager()
    session = mgr.get_session(session_id)

    if not session:
        return {"session_id": session_id, "status": "not_active"}

    vision = get_vision_orchestrator().get_health()

    return {
        "session_id": session_id,
        "phase": session.phase.value,
        "vision_active": session.vision_active,
        "audio_active": session.audio_active,
        "agents_active": session.agents_active,
        "cameras_connected": session.cameras_connected,
        "duration_minutes": round(
            (__import__("time").time() - session.start_time) / 60, 1
        ) if session.start_time else 0,
        "vision": vision,
    }

