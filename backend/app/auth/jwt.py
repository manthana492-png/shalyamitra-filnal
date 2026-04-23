"""
ShalyaMitra — JWT Authentication

Validates Supabase-issued JWTs so the backend can authenticate
requests from the frontend without running its own auth server.
"""

from __future__ import annotations
from typing import Optional
from uuid import UUID

import jwt
from fastapi import HTTPException, Header, Depends
from pydantic import BaseModel

from app.config import settings


class AuthUser(BaseModel):
    """Decoded JWT payload — minimal fields we need."""
    sub: UUID               # Supabase user ID
    email: Optional[str] = None
    role: str = "authenticated"


def decode_supabase_jwt(token: str) -> AuthUser:
    """Decode and validate a Supabase JWT."""
    if not settings.supabase_jwt_secret:
        # In dev/demo mode without a secret, return a mock user
        return AuthUser(sub=UUID("00000000-0000-0000-0000-000000000000"), email="demo@shalyamitra.dev", role="authenticated")
    try:
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            audience="authenticated",
            options={"verify_exp": True},
        )
        return AuthUser(
            sub=UUID(payload["sub"]),
            email=payload.get("email"),
            role=payload.get("role", "authenticated"),
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")


async def get_current_user(
    authorization: Optional[str] = Header(None),
    apikey: Optional[str] = Header(None, alias="apikey"),
) -> AuthUser:
    """
    FastAPI dependency — extracts user from:
      1. Authorization: Bearer <jwt>
      2. apikey header (Supabase anon key fallback for WS)
    """
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
    elif apikey:
        token = apikey

    if not token:
        # Demo mode — allow unauthenticated access
        if settings.gpu_provider.value == "demo":
            return AuthUser(sub=UUID("00000000-0000-0000-0000-000000000000"), email="demo@shalyamitra.dev")
        raise HTTPException(status_code=401, detail="Missing authentication token")

    return decode_supabase_jwt(token)
