"""
ShalyaMitra — Vision Pipeline Orchestrator

Coordinates the primary (Holoscan) and fallback (cloud VLM) vision
pipelines. Automatically switches between them based on availability.

Pipeline modes:
  1. HOLOSCAN_LIVE   — Full Holoscan on H100 (30 FPS, real-time)
  2. FALLBACK_VLM    — Cloud VLM frame analysis (every 2-5 sec)
  3. HYBRID          — Holoscan for cam3, fallback for cam1/cam2
  4. OFFLINE         — Local OpenCV only (no cloud, no GPU)

The orchestrator:
  - Probes Holoscan health at startup
  - Falls back to VLM automatically on Holoscan failure
  - Can run hybrid mode (some cameras on Holoscan, others on VLM)
  - Routes all vision results to the agent orchestrator
  - Converts VLM results into the same ServerEvent format as Holoscan
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

from app.config import settings
from app.camera.manager import (
    CameraFrame, CameraId, CameraManager, get_camera_manager,
)
from app.camera.vision_fallback import (
    VisionFallbackPipeline, VisionResult, VisionEngine, get_vision_fallback,
)
from app.agents.orchestrator import AgentEvent, EventType


class PipelineMode(str, Enum):
    HOLOSCAN_LIVE = "holoscan_live"
    FALLBACK_VLM = "fallback_vlm"
    HYBRID = "hybrid"
    OFFLINE = "offline"


@dataclass
class PipelineHealth:
    mode: PipelineMode
    holoscan_available: bool
    holoscan_fps: float
    fallback_active: bool
    fallback_engine: Optional[str]
    cameras_on_holoscan: list[str]
    cameras_on_fallback: list[str]
    total_frames_processed: int
    avg_latency_ms: float


class VisionOrchestrator:
    """
    Coordinates all vision processing — Holoscan + fallback.

    At session start:
      1. Probe Holoscan health
      2. If available → HOLOSCAN_LIVE mode
      3. If unavailable → FALLBACK_VLM mode
      4. If partial → HYBRID mode
      5. Start frame routing
    """

    def __init__(self):
        self._mode = PipelineMode.OFFLINE
        self._holoscan_available = False
        self._holoscan_url: Optional[str] = None
        self._fallback = get_vision_fallback()
        self._camera_mgr = get_camera_manager()
        self._event_callback: Optional[Any] = None
        self._total_processed = 0
        self._running = False

    def set_event_callback(self, callback):
        """Set callback to send vision events to agent orchestrator."""
        self._event_callback = callback

    async def start(self, session_id: str):
        """Start vision processing for a surgery session."""
        self._running = True

        # Step 1: Probe Holoscan
        self._holoscan_available = await self._probe_holoscan()

        if self._holoscan_available:
            self._mode = PipelineMode.HOLOSCAN_LIVE
            print(f"[VISION] Holoscan available — LIVE mode")
        else:
            self._mode = PipelineMode.FALLBACK_VLM
            print(f"[VISION] Holoscan unavailable — FALLBACK VLM mode")

            # Start fallback pipeline
            self._fallback.set_result_callback(
                lambda result: self._handle_vision_result(result, session_id)
            )
            await self._fallback.start()

        # Register frame handlers on all cameras
        for cam_id in [CameraId.CAM1_MONITOR.value, CameraId.CAM2_SENTINEL.value, CameraId.CAM3_SURGEON.value]:
            self._camera_mgr.register_frame_callback(cam_id, self._on_frame)

        # Start health monitor
        asyncio.create_task(self._health_monitor_loop())

    async def stop(self):
        """Stop all vision processing."""
        self._running = False
        await self._fallback.stop()

    async def _on_frame(self, frame: CameraFrame):
        """Handle incoming frame from any camera."""
        if self._mode == PipelineMode.HOLOSCAN_LIVE:
            # Forward to Holoscan via internal bus
            await self._forward_to_holoscan(frame)
        elif self._mode == PipelineMode.FALLBACK_VLM:
            # Buffer for periodic VLM analysis
            self._fallback.buffer_frame(frame)
        elif self._mode == PipelineMode.HYBRID:
            # Cam3 to Holoscan, others to fallback
            if frame.camera_id == CameraId.CAM3_SURGEON.value and self._holoscan_available:
                await self._forward_to_holoscan(frame)
            else:
                self._fallback.buffer_frame(frame)

    async def _forward_to_holoscan(self, frame: CameraFrame):
        """Forward frame to Holoscan runtime."""
        # TODO: Implement when Holoscan container is running
        # This will send frames via shared memory or gRPC to the Holoscan graph
        pass

    async def _handle_vision_result(self, result: VisionResult, session_id: str):
        """Convert VisionResult to AgentEvents and dispatch."""
        if not self._event_callback:
            return

        self._total_processed += 1
        events: list[AgentEvent] = []

        # ── Camera 1: Vitals OCR ──────────────────────────
        if result.camera_id == CameraId.CAM1_MONITOR.value and result.vitals_ocr:
            v = result.vitals_ocr
            if any(v.get(k) is not None for k in ["hr", "spo2", "map"]):
                events.append(AgentEvent(
                    type=EventType.VITALS_UPDATE,
                    source="vision_fallback",
                    session_id=session_id,
                    priority=5,
                    data={
                        "hr": v.get("hr", 0),
                        "spo2": v.get("spo2", 0),
                        "map": v.get("map", 0),
                        "etco2": v.get("etco2", 0),
                        "temp": v.get("temp", 36.5),
                        "rr": v.get("rr", 14),
                        "at": result.timestamp,
                        "engine": result.engine_used.value,
                    },
                ))

        # ── Camera 2: Instruments ─────────────────────────
        if result.camera_id == CameraId.CAM2_SENTINEL.value and result.instruments:
            events.append(AgentEvent(
                type=EventType.INSTRUMENT_DETECTED,
                source="vision_fallback",
                session_id=session_id,
                priority=7,
                data={
                    "instruments": result.instruments,
                    "detections": result.detections,
                    "at": result.timestamp,
                    "engine": result.engine_used.value,
                },
            ))

        # ── Camera 3: Surgical field ──────────────────────
        if result.camera_id == CameraId.CAM3_SURGEON.value:
            # Phase change
            if result.phase:
                events.append(AgentEvent(
                    type=EventType.PHASE_CHANGE,
                    source="vision_fallback",
                    session_id=session_id,
                    priority=6,
                    data={
                        "phase": result.phase,
                        "confidence": result.phase_confidence,
                        "at": result.timestamp,
                    },
                ))

            # HAEMORRHAGE — Critical priority
            if result.haemorrhage_detected and result.haemorrhage_confidence > 0.7:
                events.append(AgentEvent(
                    type=EventType.HAEMORRHAGE_DETECTED,
                    source="vision_fallback",
                    session_id=session_id,
                    priority=1,  # CRITICAL
                    data={
                        "confidence": result.haemorrhage_confidence,
                        "pattern": result.haemorrhage_pattern or "unknown",
                        "location": "surgical field",
                        "at": result.timestamp,
                        "engine": result.engine_used.value,
                    },
                ))

            # Anatomy detection
            if result.anatomy_labels:
                events.append(AgentEvent(
                    type=EventType.ANATOMY_DETECTED,
                    source="vision_fallback",
                    session_id=session_id,
                    priority=7,
                    data={
                        "labels": result.anatomy_labels,
                        "at": result.timestamp,
                    },
                ))

        # Dispatch all events
        for event in events:
            await self._event_callback(event)

    async def _probe_holoscan(self) -> bool:
        """Check if Holoscan runtime is available."""
        if settings.gpu_provider.value == "demo":
            return False  # No Holoscan in demo mode

        try:
            import httpx
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.get(
                    f"{settings.gpu_backend_url or 'http://localhost:9100'}/health"
                )
                return resp.status_code == 200
        except Exception:
            return False

    async def _health_monitor_loop(self):
        """Periodically check Holoscan health and switch modes if needed."""
        while self._running:
            await asyncio.sleep(30.0)

            was_available = self._holoscan_available
            self._holoscan_available = await self._probe_holoscan()

            # Holoscan came back online
            if not was_available and self._holoscan_available:
                self._mode = PipelineMode.HOLOSCAN_LIVE
                await self._fallback.stop()
                print("[VISION] Holoscan recovered -- switching to LIVE mode")

            # Holoscan went down
            elif was_available and not self._holoscan_available:
                self._mode = PipelineMode.FALLBACK_VLM
                await self._fallback.start()
                print("[VISION] Holoscan failed -- switching to FALLBACK VLM mode")

    def get_health(self) -> dict:
        fallback_stats = self._fallback.get_stats()
        cameras = self._camera_mgr.get_all_status()

        cameras_holoscan = []
        cameras_fallback = []
        for cam in cameras:
            if self._mode == PipelineMode.HOLOSCAN_LIVE:
                cameras_holoscan.append(cam["camera_id"])
            elif self._mode == PipelineMode.HYBRID and cam["camera_id"] == "cam3":
                cameras_holoscan.append(cam["camera_id"])
            else:
                cameras_fallback.append(cam["camera_id"])

        return {
            "mode": self._mode.value,
            "holoscan_available": self._holoscan_available,
            "fallback_active": self._mode in (PipelineMode.FALLBACK_VLM, PipelineMode.HYBRID),
            "fallback_engines": fallback_stats.get("engines_healthy", {}),
            "cameras_on_holoscan": cameras_holoscan,
            "cameras_on_fallback": cameras_fallback,
            "capture_intervals": fallback_stats.get("capture_intervals", {}),
            "total_analyses": fallback_stats.get("analyses_performed", 0),
            "avg_latency_ms": fallback_stats.get("avg_latency_ms", 0),
            "cameras": cameras,
        }


# Singleton
_orchestrator: Optional[VisionOrchestrator] = None


def get_vision_orchestrator() -> VisionOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = VisionOrchestrator()
    return _orchestrator
