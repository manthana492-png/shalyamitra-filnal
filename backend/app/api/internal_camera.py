"""Internal ingress for camera JPEG/PNG frames (Holoscan-bridge + vision pipeline)."""

from __future__ import annotations

import base64
import time
from typing import Optional

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from app.config import settings
from app.camera.manager import CameraFrame, get_camera_manager

router = APIRouter()


class CameraFrameIn(BaseModel):
    session_id: str = ""
    camera_id: str = Field(..., description="cam1 | cam2 | cam3")
    image_b64: str
    mime_type: str = "image/jpeg"


def _verify_internal(x_internal_token: Optional[str]) -> None:
    tok = settings.internal_bus_token
    if not tok:
        return
    if x_internal_token != tok:
        raise HTTPException(status_code=401, detail="Invalid internal token")


@router.post("/camera/frame")
async def ingest_camera_frame(
    body: CameraFrameIn,
    x_internal_token: Optional[str] = Header(None, alias="X-Internal-Token"),
):
    """Receive one frame from holoscan-bridge / ingest workers into CameraManager."""
    _verify_internal(x_internal_token)
    try:
        raw = base64.b64decode(body.image_b64)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid base64: {exc}") from exc

    frame = CameraFrame(
        camera_id=body.camera_id,
        data=raw,
        mime_type=body.mime_type or "image/jpeg",
        timestamp=time.time(),
    )
    await get_camera_manager().on_frame(frame)
    return {"status": "ok", "camera_id": body.camera_id, "bytes": len(raw)}
