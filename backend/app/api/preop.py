"""
ShalyaMitra — Pre-Operative Analysis API (The Scholar)

Triggers Scholar-backed structured clinical synthesis for the PreOpView page.
"""

from __future__ import annotations

from typing import Dict

from fastapi import APIRouter, Depends, HTTPException

from app.auth.jwt import get_current_user, AuthUser
from app.models.schemas import PreOpRequest, PreOpAnalysis
from app.api.sessions import peek_session_record
from app.services.preop_scholar import generate_preop_analysis, PreopGenerationError

router = APIRouter()

_PREOP_CACHE: Dict[str, PreOpAnalysis] = {}


@router.post("/analyse", response_model=PreOpAnalysis)
async def analyse_preop(
    body: PreOpRequest,
    user: AuthUser = Depends(get_current_user),
):
    """Generate or regenerate structured pre-operative analysis (Scholar + RAG)."""
    payload = body.model_dump()
    sid = payload.pop("session_id", "")
    meta = peek_session_record(sid) or {}
    # Carry optional contextual keys forwarded by the client alongside session_id.
    extras = {k: v for k, v in payload.items() if v not in (None, "", [])}
    merged_ctx = {**meta, **extras}

    try:
        analysis = await generate_preop_analysis(sid, merged_ctx or None)
    except PreopGenerationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    _PREOP_CACHE[sid] = analysis
    return analysis


@router.get("/{session_id}", response_model=PreOpAnalysis)
async def get_preop_analysis(
    session_id: str,
    user: AuthUser = Depends(get_current_user),
):
    """Retrieve cached analysis or synthesise one on-demand."""
    cached = _PREOP_CACHE.get(session_id)
    if cached:
        return cached
    meta = peek_session_record(session_id)
    try:
        analysis = await generate_preop_analysis(session_id, meta)
    except PreopGenerationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    _PREOP_CACHE[session_id] = analysis
    return analysis
