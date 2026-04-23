"""
ShalyaMitra — Camera Connection Manager

Manages all 3 surgical cameras with multiple connection methods:

  Camera 1 (Monitor Sentinel):
    - Android phone on tripod pointing at patient monitor
    - USB webcam as fallback
    - LiveKit video track OR WebRTC direct

  Camera 2 (The Sentinel):
    - Android phone overhead on boom arm (instruments/swabs)
    - GoPro via Wi-Fi/USB
    - Mobile browser (WebRTC from phone's browser)

  Camera 3 (Surgeon's Eye):
    - Android phone on head mount / laparoscope
    - GoPro Hero on headband
    - Mobile phone camera via browser (fallback)
    - USB laparoscope feed

Connection Priority per camera:
  1. LiveKit native (Android app with LiveKit SDK)  — best quality, lowest latency
  2. WebRTC browser (phone opens URL, shares camera) — no app install needed
  3. USB/HDMI capture device (GoPro, laparoscope)    — wired, reliable
  4. RTSP stream (IP camera / GoPro Wi-Fi)           — wireless, higher latency

Each camera can independently use any connection method.
The system auto-detects available cameras and assigns them.
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, Callable
from uuid import uuid4


class CameraId(str, Enum):
    CAM1_MONITOR = "cam1"      # Patient monitor
    CAM2_SENTINEL = "cam2"     # Instrument tray (overhead)
    CAM3_SURGEON = "cam3"      # Surgeon's eye / laparoscope


class ConnectionMethod(str, Enum):
    LIVEKIT = "livekit"                 # LiveKit SDK (Android app)
    WEBRTC_BROWSER = "webrtc_browser"   # Phone browser shares camera
    USB_CAPTURE = "usb_capture"         # USB/HDMI capture card
    RTSP = "rtsp"                       # IP camera / GoPro Wi-Fi
    MOCK = "mock"                       # Test pattern / demo mode


class CameraStatus(str, Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    STREAMING = "streaming"
    ERROR = "error"
    RECONNECTING = "reconnecting"


@dataclass
class CameraConfig:
    """Configuration for a single camera slot."""
    camera_id: CameraId
    label: str
    description: str
    connection: ConnectionMethod = ConnectionMethod.MOCK
    status: CameraStatus = CameraStatus.DISCONNECTED
    resolution: str = "1280x720"
    fps: int = 30
    # Connection-specific params
    livekit_track_id: Optional[str] = None
    webrtc_peer_id: Optional[str] = None
    usb_device_path: Optional[str] = None
    rtsp_url: Optional[str] = None
    # Health tracking
    last_frame_at: float = 0.0
    frames_received: int = 0
    reconnect_attempts: int = 0
    max_reconnect_attempts: int = 5
    error_message: Optional[str] = None


@dataclass
class CameraFrame:
    """A single captured frame from any camera."""
    camera_id: str
    data: bytes                 # Raw frame bytes (JPEG/PNG)
    mime_type: str = "image/jpeg"
    width: int = 1280
    height: int = 720
    timestamp: float = 0.0
    frame_number: int = 0


# ══════════════════════════════════════════════════════════
# Default Camera Configurations
# ══════════════════════════════════════════════════════════

DEFAULT_CAMERAS: dict[CameraId, CameraConfig] = {
    CameraId.CAM1_MONITOR: CameraConfig(
        camera_id=CameraId.CAM1_MONITOR,
        label="Monitor Sentinel",
        description="Patient monitor — reads vital signs via OCR. Place Android phone or webcam facing the monitor display.",
        resolution="1920x1080",  # Higher res for OCR accuracy
        fps=2,                   # OCR only needs 2 FPS
    ),
    CameraId.CAM2_SENTINEL: CameraConfig(
        camera_id=CameraId.CAM2_SENTINEL,
        label="The Sentinel",
        description="Overhead view of instrument tray and swab area. Mount Android phone or GoPro on boom arm.",
        resolution="1280x720",
        fps=5,                   # Instrument counting needs moderate FPS
    ),
    CameraId.CAM3_SURGEON: CameraConfig(
        camera_id=CameraId.CAM3_SURGEON,
        label="Surgeon's Eye",
        description="Surgical field view. Mount phone on headband, use GoPro Hero, or connect laparoscope.",
        resolution="1920x1080",
        fps=30,                  # Full FPS for real-time analysis
    ),
}


class CameraManager:
    """
    Central camera manager — handles connections, health monitoring,
    auto-reconnection, and frame distribution.
    """

    def __init__(self):
        self.cameras: dict[str, CameraConfig] = {
            cam_id.value: config for cam_id, config in DEFAULT_CAMERAS.items()
        }
        self._frame_callbacks: dict[str, list[Callable]] = {}
        self._health_task: Optional[asyncio.Task] = None
        self._join_codes: dict[str, str] = {}  # camera_id -> join URL for mobile

    # ── Connection Methods ────────────────────────────────

    async def connect_camera(
        self,
        camera_id: str,
        method: ConnectionMethod,
        **kwargs,
    ) -> dict:
        """
        Connect a camera using the specified method.

        Returns connection details including:
        - For WebRTC browser: a join URL the surgeon scans with QR code
        - For LiveKit: the track ID to subscribe to
        - For USB: the device path
        """
        cam = self.cameras.get(camera_id)
        if not cam:
            return {"error": f"Unknown camera: {camera_id}"}

        cam.connection = method
        cam.status = CameraStatus.CONNECTING
        cam.reconnect_attempts = 0
        cam.error_message = None

        if method == ConnectionMethod.LIVEKIT:
            return await self._connect_livekit(cam, **kwargs)
        elif method == ConnectionMethod.WEBRTC_BROWSER:
            return await self._connect_webrtc_browser(cam, **kwargs)
        elif method == ConnectionMethod.USB_CAPTURE:
            return await self._connect_usb(cam, **kwargs)
        elif method == ConnectionMethod.RTSP:
            return await self._connect_rtsp(cam, **kwargs)
        elif method == ConnectionMethod.MOCK:
            cam.status = CameraStatus.STREAMING
            return {"status": "connected", "method": "mock", "camera_id": camera_id}

        return {"error": f"Unknown method: {method}"}

    async def _connect_livekit(self, cam: CameraConfig, **kwargs) -> dict:
        """
        Connect via LiveKit SDK.
        The Android companion app publishes a video track to the LiveKit room.
        We subscribe to that track here.
        """
        from app.config import settings

        cam.livekit_track_id = kwargs.get("track_id", f"{cam.camera_id.value}_track")

        # Generate LiveKit room token for this camera
        # In production: use livekit-api to create a token
        room_name = kwargs.get("room_name", "surgery_room")

        cam.status = CameraStatus.CONNECTED
        return {
            "status": "connected",
            "method": "livekit",
            "camera_id": cam.camera_id.value,
            "livekit_url": settings.livekit_url,
            "room_name": room_name,
            "track_id": cam.livekit_track_id,
            # Token for Android app to join
            "participant_token": f"lk_token_{cam.camera_id.value}_{uuid4().hex[:8]}",
        }

    async def _connect_webrtc_browser(self, cam: CameraConfig, **kwargs) -> dict:
        """
        Connect via phone browser — no app install needed.

        Generates a unique URL that the surgeon/nurse opens on
        the phone's browser. The browser shares its camera via WebRTC.
        This is the easiest connection method — just scan a QR code.
        """
        join_code = uuid4().hex[:8]
        self._join_codes[cam.camera_id.value] = join_code

        # The frontend serves a lightweight camera-sharing page at this URL
        base_url = kwargs.get("base_url", "https://shalyamitra.dev")
        join_url = f"{base_url}/camera/join/{join_code}?cam={cam.camera_id.value}"

        cam.webrtc_peer_id = join_code
        cam.status = CameraStatus.CONNECTING  # Waiting for phone to connect

        return {
            "status": "waiting_for_device",
            "method": "webrtc_browser",
            "camera_id": cam.camera_id.value,
            "join_url": join_url,
            "join_code": join_code,
            "qr_data": join_url,  # Frontend generates QR from this
            "instructions": (
                f"Open this URL on the phone camera for {cam.label}. "
                f"Or scan the QR code. The browser will ask for camera permission."
            ),
        }

    async def _connect_usb(self, cam: CameraConfig, **kwargs) -> dict:
        """Connect via USB/HDMI capture device (GoPro, laparoscope)."""
        device_path = kwargs.get("device_path", "/dev/video0")
        cam.usb_device_path = device_path
        cam.status = CameraStatus.CONNECTED
        return {
            "status": "connected",
            "method": "usb_capture",
            "camera_id": cam.camera_id.value,
            "device_path": device_path,
        }

    async def _connect_rtsp(self, cam: CameraConfig, **kwargs) -> dict:
        """Connect via RTSP stream (IP camera, GoPro Wi-Fi)."""
        rtsp_url = kwargs.get("rtsp_url", "rtsp://192.168.1.100:8554/live")
        cam.rtsp_url = rtsp_url
        cam.status = CameraStatus.CONNECTED
        return {
            "status": "connected",
            "method": "rtsp",
            "camera_id": cam.camera_id.value,
            "rtsp_url": rtsp_url,
        }

    async def disconnect_camera(self, camera_id: str):
        """Disconnect a camera and clean up resources."""
        cam = self.cameras.get(camera_id)
        if cam:
            cam.status = CameraStatus.DISCONNECTED
            cam.livekit_track_id = None
            cam.webrtc_peer_id = None
            self._join_codes.pop(camera_id, None)

    # ── Frame Handling ────────────────────────────────────

    async def on_frame(self, frame: CameraFrame):
        """
        Called when a frame is received from any camera.
        Distributes to all registered callbacks (vision pipeline, fallback, etc.)
        """
        cam = self.cameras.get(frame.camera_id)
        if cam:
            cam.last_frame_at = time.time()
            cam.frames_received += 1
            cam.status = CameraStatus.STREAMING

        callbacks = self._frame_callbacks.get(frame.camera_id, [])
        for cb in callbacks:
            try:
                await cb(frame)
            except Exception as e:
                print(f"Frame callback error for {frame.camera_id}: {e}")

    def register_frame_callback(self, camera_id: str, callback: Callable):
        """Register a callback to receive frames from a camera."""
        if camera_id not in self._frame_callbacks:
            self._frame_callbacks[camera_id] = []
        self._frame_callbacks[camera_id].append(callback)

    # ── Health Monitoring ─────────────────────────────────

    async def start_health_monitor(self):
        """Start background health monitoring for all cameras."""
        self._health_task = asyncio.create_task(self._health_loop())

    async def _health_loop(self):
        """Check camera health every 5 seconds."""
        while True:
            await asyncio.sleep(5.0)
            now = time.time()
            for cam_id, cam in self.cameras.items():
                if cam.status not in (CameraStatus.STREAMING, CameraStatus.CONNECTED):
                    continue

                # Check for stale frames (no frame in 10 seconds)
                if cam.last_frame_at > 0 and (now - cam.last_frame_at) > 10.0:
                    cam.status = CameraStatus.RECONNECTING
                    cam.reconnect_attempts += 1

                    if cam.reconnect_attempts <= cam.max_reconnect_attempts:
                        print(f"Camera {cam_id} stale — reconnecting (attempt {cam.reconnect_attempts})")
                        await self.connect_camera(cam_id, cam.connection)
                    else:
                        cam.status = CameraStatus.ERROR
                        cam.error_message = f"Camera disconnected after {cam.max_reconnect_attempts} reconnect attempts"
                        print(f"Camera {cam_id} FAILED — max reconnects reached")

    # ── Status ────────────────────────────────────────────

    def get_all_status(self) -> list[dict]:
        """Get status of all cameras for the API/frontend."""
        return [
            {
                "camera_id": cam.camera_id.value,
                "label": cam.label,
                "description": cam.description,
                "connection": cam.connection.value,
                "status": cam.status.value,
                "resolution": cam.resolution,
                "fps": cam.fps,
                "frames_received": cam.frames_received,
                "last_frame_age_seconds": round(time.time() - cam.last_frame_at, 1) if cam.last_frame_at > 0 else None,
                "reconnect_attempts": cam.reconnect_attempts,
                "error": cam.error_message,
                "join_url": None,  # Only populated for webrtc_browser
            }
            for cam in self.cameras.values()
        ]

    def get_camera_status(self, camera_id: str) -> Optional[dict]:
        statuses = self.get_all_status()
        for s in statuses:
            if s["camera_id"] == camera_id:
                return s
        return None


# Singleton
_manager: Optional[CameraManager] = None


def get_camera_manager() -> CameraManager:
    global _manager
    if _manager is None:
        _manager = CameraManager()
    return _manager
