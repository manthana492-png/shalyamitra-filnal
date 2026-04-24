"""
Internal Holoscan / HoloHub event ingress (service-to-service).

holoscan-bridge (or a future HoloHub process) POSTs vision events here.
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from app.config import settings
from app.agents.orchestrator import (
    AgentEvent,
    EventType,
    get_orchestrator,
)


router = APIRouter()


class HoloscanVisionEvent(BaseModel):
    """Payload from HoloHub / Holoscan graphs (tool detect, out-of-body, etc.)."""

    session_id: str
    event_type: str = Field(
        ...,
        description="instrument_detected | phase | ood | haemorrhage | overlay | ping",
    )
    source: str = "holoscan"
    camera_id: Optional[str] = None
    priority: int = 6
    data: dict[str, Any] = Field(default_factory=dict)


def _verify_internal(x_internal_token: Optional[str]) -> None:
    tok = settings.internal_bus_token
    if not tok:
        return
    if x_internal_token != tok:
        raise HTTPException(status_code=401, detail="Invalid internal token")


def _map_event_type(name: str) -> EventType:
    n = name.lower().strip()
    mapping = {
        "instrument_detected": EventType.INSTRUMENT_DETECTED,
        "instrument": EventType.INSTRUMENT_DETECTED,
        "anatomy": EventType.ANATOMY_DETECTED,
        "anatomy_detected": EventType.ANATOMY_DETECTED,
        "haemorrhage": EventType.HAEMORRHAGE_DETECTED,
        "haemorrhage_detected": EventType.HAEMORRHAGE_DETECTED,
        "phase": EventType.PHASE_CHANGE,
        "phase_change": EventType.PHASE_CHANGE,
        "vitals": EventType.VITALS_UPDATE,
        "transcript": EventType.TRANSCRIPT,
        "ping": EventType.DISPLAY_VISION,
    }
    return mapping.get(n, EventType.DISPLAY_VISION)


@router.post("/holoscan/vision")
async def ingest_holoscan_vision(
    body: HoloscanVisionEvent,
    x_internal_token: Optional[str] = Header(None, alias="X-Internal-Token"),
):
    """Receive a vision event from holoscan-bridge / HoloHub and dispatch on ShalyaBus."""
    _verify_internal(x_internal_token)

    orch = get_orchestrator(register_all=True)
    et = _map_event_type(body.event_type)
    event = AgentEvent(
        type=et,
        source=body.source,
        session_id=body.session_id,
        priority=body.priority,
        data={
            "camera_id": body.camera_id,
            "ingest": settings.video_ingest_mode,
            **body.data,
        },
    )
    await orch.dispatch(event)
    return {"status": "dispatched", "event_type": et.value}
