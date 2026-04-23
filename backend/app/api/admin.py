"""
ShalyaMitra — Admin API

Endpoints for the admin panel: audit log, user management,
GPU instance monitoring. The frontend has AdminAudit, AdminUsers,
and AdminGpu pages that consume these.
"""

from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from app.auth.jwt import get_current_user, AuthUser

router = APIRouter()


@router.get("/audit")
async def get_audit_log(
    user: AuthUser = Depends(get_current_user),
    limit: int = 50,
    offset: int = 0,
):
    """Get audit log entries. Admin only."""
    # TODO: Fetch from Supabase audit_log table
    return {"entries": [], "total": 0}


@router.get("/users")
async def list_users(
    user: AuthUser = Depends(get_current_user),
):
    """List all users. Admin only."""
    # TODO: Fetch from Supabase profiles + user_roles
    return {"users": []}


@router.get("/gpu/status")
async def gpu_status(
    user: AuthUser = Depends(get_current_user),
):
    """Get current GPU instance status."""
    from app.config import settings
    return {
        "provider": settings.gpu_provider.value,
        "active_sessions": 0,
        "instances": [],
    }


@router.post("/gpu/provision")
async def provision_gpu(
    user: AuthUser = Depends(get_current_user),
):
    """Manually provision a GPU instance. Admin only."""
    # TODO: Wire to GPU orchestrator
    return {"status": "not_implemented", "message": "GPU orchestrator pending Phase 2"}
