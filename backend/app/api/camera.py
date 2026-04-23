"""
ShalyaMitra — Camera Management API

Endpoints for:
  1. List all cameras and their status
  2. Connect a camera (LiveKit / WebRTC browser / USB / RTSP)
  3. Get QR code data for mobile browser camera
  4. Disconnect a camera
  5. Vision pipeline health (Holoscan vs fallback)
  6. Adjust capture intervals for fallback mode
"""

from __future__ import annotations
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.auth.jwt import get_current_user, AuthUser
from app.camera.manager import get_camera_manager, ConnectionMethod
from app.camera.vision_orchestrator import get_vision_orchestrator

router = APIRouter()


class CameraConnectRequest(BaseModel):
    camera_id: str  # "cam1" | "cam2" | "cam3"
    method: str     # "livekit" | "webrtc_browser" | "usb_capture" | "rtsp" | "mock"
    # Optional connection params
    track_id: Optional[str] = None
    room_name: Optional[str] = None
    device_path: Optional[str] = None
    rtsp_url: Optional[str] = None
    base_url: Optional[str] = None


class CaptureIntervalUpdate(BaseModel):
    camera_id: str
    interval_seconds: float  # 1.0 to 30.0


@router.get("/status")
async def camera_status(user: AuthUser = Depends(get_current_user)):
    """
    Get status of all 3 cameras.
    Shows connection method, streaming status, frame count, and errors.
    """
    mgr = get_camera_manager()
    return {
        "cameras": mgr.get_all_status(),
        "connection_methods": [
            {
                "id": "livekit",
                "name": "LiveKit SDK (Android App)",
                "description": "Best quality. Install ShalyaMitra Camera app on Android phone.",
                "requires_app": True,
            },
            {
                "id": "webrtc_browser",
                "name": "Phone Browser (QR Code)",
                "description": "No app needed. Scan QR code with phone camera — opens browser and shares camera.",
                "requires_app": False,
            },
            {
                "id": "usb_capture",
                "name": "USB / HDMI Capture",
                "description": "Connect GoPro or laparoscope via USB/HDMI capture card.",
                "requires_app": False,
            },
            {
                "id": "rtsp",
                "name": "IP Camera / RTSP Stream",
                "description": "Connect IP camera or GoPro via Wi-Fi RTSP stream.",
                "requires_app": False,
            },
            {
                "id": "mock",
                "name": "Demo / Test Pattern",
                "description": "Simulated camera feed for testing.",
                "requires_app": False,
            },
        ],
    }


@router.post("/connect")
async def connect_camera(
    body: CameraConnectRequest,
    user: AuthUser = Depends(get_current_user),
):
    """
    Connect a camera using the specified method.

    For 'webrtc_browser': Returns a join URL and QR code data.
    The surgeon/nurse scans the QR on the phone to share the camera.

    For 'livekit': Returns a LiveKit room token.
    The Android app uses this to join and publish video.
    """
    mgr = get_camera_manager()

    try:
        method = ConnectionMethod(body.method)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Unknown method: {body.method}")

    result = await mgr.connect_camera(
        camera_id=body.camera_id,
        method=method,
        track_id=body.track_id,
        room_name=body.room_name or "surgery_room",
        device_path=body.device_path,
        rtsp_url=body.rtsp_url,
        base_url=body.base_url or "https://shalyamitra.dev",
    )

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


@router.post("/disconnect/{camera_id}")
async def disconnect_camera(
    camera_id: str,
    user: AuthUser = Depends(get_current_user),
):
    """Disconnect a camera."""
    mgr = get_camera_manager()
    await mgr.disconnect_camera(camera_id)
    return {"status": "disconnected", "camera_id": camera_id}


@router.get("/vision/health")
async def vision_health(user: AuthUser = Depends(get_current_user)):
    """
    Get vision pipeline health.
    Shows whether Holoscan or fallback VLM is active,
    which engines are healthy, and capture intervals.
    """
    orch = get_vision_orchestrator()
    return orch.get_health()


@router.post("/vision/interval")
async def set_capture_interval(
    body: CaptureIntervalUpdate,
    user: AuthUser = Depends(get_current_user),
):
    """
    Adjust the frame capture interval for fallback VLM analysis.
    Lower interval = more frequent analysis but higher API cost.

    Recommended:
      - cam1 (monitor): 3-5 seconds (vitals change slowly)
      - cam2 (instruments): 5-10 seconds (instrument changes are infrequent)
      - cam3 (surgical field): 1-3 seconds (most critical)
    """
    from app.camera.vision_fallback import get_vision_fallback

    if body.interval_seconds < 1.0 or body.interval_seconds > 30.0:
        raise HTTPException(status_code=400, detail="Interval must be 1.0-30.0 seconds")

    fallback = get_vision_fallback()
    fallback._capture_intervals[body.camera_id] = body.interval_seconds

    return {
        "status": "updated",
        "camera_id": body.camera_id,
        "interval_seconds": body.interval_seconds,
    }


@router.get("/qr/{camera_id}")
async def get_camera_qr(
    camera_id: str,
    user: AuthUser = Depends(get_current_user),
):
    """
    Get QR code data for connecting a camera via phone browser.
    Frontend generates the QR from this URL.

    Usage:
      1. Call POST /connect with method=webrtc_browser first
      2. Then GET this endpoint for the QR URL
      3. Display QR on the theatre display
      4. Nurse scans QR with phone → browser opens → shares camera
    """
    mgr = get_camera_manager()
    status = mgr.get_camera_status(camera_id)
    if not status:
        raise HTTPException(status_code=404, detail=f"Camera {camera_id} not found")

    join_code = mgr._join_codes.get(camera_id)
    if not join_code:
        raise HTTPException(status_code=400, detail="Camera not configured for browser connection. Call POST /connect with method=webrtc_browser first.")

    return {
        "camera_id": camera_id,
        "label": status.get("label", camera_id),
        "join_url": f"https://shalyamitra.dev/camera/join/{join_code}?cam={camera_id}",
        "join_code": join_code,
        "instructions": f"Scan this QR code with the phone for {status.get('label', camera_id)}. Allow camera access when prompted.",
    }
