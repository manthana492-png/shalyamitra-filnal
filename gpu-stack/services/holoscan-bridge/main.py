"""
Holoscan bridge — HTTP face for HoloHub / Holoscan event ingress.

- Serves /health for vision_orchestrator probes.
- Receives video ingest mode: webrtc (phones/LiveKit) or hsb (Sensor Bridge).
- Forwards HoloHub-style events to the agent ShalyaBus (POST /api/internal/...).
"""

from __future__ import annotations

import os
from typing import Any, Optional

import httpx
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="ShalyaMitra Holoscan Bridge", version="1.0.0")

VIDEO_INGEST_MODE = os.environ.get("VIDEO_INGEST_MODE", "webrtc")
AGENT_BASE = os.environ.get("AGENT_BASE_URL", "http://agent-orchestrator:9000")
INTERNAL_TOKEN = os.environ.get("INTERNAL_BUS_TOKEN", "")


class SurgicalEventIn(BaseModel):
    session_id: str
    event_type: str = Field(..., description="instrument_detected | phase | ood | haemorrhage | overlay | ping")
    source: str = "holoscan"
    camera_id: Optional[str] = None
    priority: int = 6
    data: dict[str, Any] = Field(default_factory=dict)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "holoscan-bridge",
        "video_ingest_mode": VIDEO_INGEST_MODE,
        "holohub": "mount pipelines under /app/pipelines in clara-holoscan; see services/holoscan/README.md",
    }


@app.get("/v1/config")
async def v1_config():
    return {
        "video_ingest_mode": VIDEO_INGEST_MODE,
        "agent_base": AGENT_BASE,
    }


def _headers(x_internal: Optional[str]) -> dict[str, str]:
    h = {"Content-Type": "application/json"}
    if INTERNAL_TOKEN:
        h["X-Internal-Token"] = INTERNAL_TOKEN
    elif x_internal:
        h["X-Internal-Token"] = x_internal
    return h


@app.post("/v1/forward")
async def forward_to_agent(
    body: SurgicalEventIn,
    x_internal_token: Optional[str] = Header(None, alias="X-Internal-Token"),
):
    """Proxy a single vision event to the agent internal API."""
    url = f"{AGENT_BASE.rstrip('/')}/api/internal/holoscan/vision"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.post(
                url,
                json=body.model_dump(),
                headers=_headers(x_internal_token),
            )
            if r.status_code >= 400:
                raise HTTPException(status_code=r.status_code, detail=r.text[:500])
            return r.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e


@app.post("/v1/surgical_event")
async def surgical_event(
    body: SurgicalEventIn,
    x_internal_token: Optional[str] = Header(None, alias="X-Internal-Token"),
):
    """Alias for forward — HoloHub-style name."""
    return await forward_to_agent(body, x_internal_token)
