"""
ShalyaMitra — Surgeon Profile API

Manages surgeon profiles and preferences. The frontend's
SurgeonProfile page reads/writes through these endpoints.
"""

from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from app.auth.jwt import get_current_user, AuthUser
from app.models.schemas import ProfileBase

router = APIRouter()


@router.get("/me")
async def get_my_profile(user: AuthUser = Depends(get_current_user)):
    """Get the current user's profile."""
    # TODO: Fetch from Supabase/PostgreSQL
    return {
        "id": str(user.sub),
        "user_id": str(user.sub),
        "full_name": "Dr. Shivalumar",
        "title": "MS, FRCS",
        "hospital": "ShalyaMitra Clinical Validation Centre",
        "avatar_url": None,
    }


@router.patch("/me")
async def update_my_profile(
    body: ProfileBase,
    user: AuthUser = Depends(get_current_user),
):
    """Update the current user's profile."""
    # TODO: Update in Supabase/PostgreSQL
    return {"status": "updated", "user_id": str(user.sub), **body.model_dump(exclude_none=True)}
