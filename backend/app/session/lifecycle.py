"""
ShalyaMitra — Session Lifecycle Manager

Manages the complete lifecycle of a surgical session:
  1. PRE-OP   → Scholar brief, Marma advisory, instrument checklist
  2. INTRA-OP → Agent orchestrator running, all 11 agents active
  3. POST-OP  → Chronicler report, handover, session archive

Coordinates:
  - GPU stack provisioning (when applicable)
  - Vision pipeline startup
  - Audio pipeline startup
  - Agent orchestrator session management
  - WebSocket state synchronization
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from app.config import settings
from app.agents.orchestrator import get_orchestrator, AgentEvent, EventType
from app.camera.manager import get_camera_manager
from app.camera.vision_orchestrator import get_vision_orchestrator


class SessionPhase(str, Enum):
    CREATED = "created"
    PRE_OP = "pre_op"
    INTRA_OP = "intra_op"
    POST_OP = "post_op"
    CLOSED = "closed"


@dataclass
class SurgerySession:
    """State for an active surgery session."""
    session_id: str
    phase: SessionPhase = SessionPhase.CREATED
    procedure: str = ""
    patient: dict[str, Any] = field(default_factory=dict)
    surgeon: str = ""
    start_time: float = 0.0
    end_time: float = 0.0
    # Pipeline status
    vision_active: bool = False
    audio_active: bool = False
    agents_active: bool = False
    # Connection tracking
    ws_connections: int = 0
    cameras_connected: int = 0
    # Phase timeline
    phase_history: list[dict] = field(default_factory=list)


class SessionManager:
    """
    Manages all active surgery sessions.
    
    Lifecycle:
      create_session() → start_preop() → start_intraop() → end_surgery() → close()
    """

    def __init__(self):
        self._sessions: dict[str, SurgerySession] = {}
        self._ws_callbacks: dict[str, list] = {}  # session_id -> [callback]

    def get_session(self, session_id: str) -> Optional[SurgerySession]:
        return self._sessions.get(session_id)

    def get_all_sessions(self) -> list[dict]:
        return [
            {
                "session_id": s.session_id,
                "phase": s.phase.value,
                "procedure": s.procedure,
                "surgeon": s.surgeon,
                "start_time": s.start_time,
                "duration_minutes": round((time.time() - s.start_time) / 60, 1) if s.start_time else 0,
                "vision_active": s.vision_active,
                "audio_active": s.audio_active,
                "agents_active": s.agents_active,
                "cameras_connected": s.cameras_connected,
            }
            for s in self._sessions.values()
        ]

    # ── Phase 1: Create ───────────────────────────────────

    async def create_session(
        self,
        session_id: str,
        procedure: str,
        patient: dict[str, Any],
        surgeon: str = "",
    ) -> SurgerySession:
        """Create a new surgery session."""
        session = SurgerySession(
            session_id=session_id,
            procedure=procedure,
            patient=patient,
            surgeon=surgeon,
        )
        self._sessions[session_id] = session
        session.phase = SessionPhase.CREATED
        session.phase_history.append({"phase": "created", "at": time.time()})
        print(f"[SESSION] Created: {session_id} — {procedure}")
        return session

    # ── Phase 2: Pre-Op ───────────────────────────────────

    async def start_preop(self, session_id: str) -> dict:
        """
        Start pre-operative phase:
          - Scholar generates surgical brief
          - Oracle loads Marma advisories
          - Instrument checklist prepared
        """
        session = self._sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}

        session.phase = SessionPhase.PRE_OP
        session.phase_history.append({"phase": "pre_op", "at": time.time()})

        # Initialize orchestrator and dispatch session start for pre-op agents
        orch = get_orchestrator()
        orch.set_display_callback(lambda event: self._broadcast_event(session_id, event))

        # Scholar and Oracle will pick up SESSION_START
        await orch.dispatch(AgentEvent(
            type=EventType.SESSION_START,
            source="session_manager",
            session_id=session_id,
            priority=3,
            data={
                "procedure": session.procedure,
                "patient": session.patient,
                "surgeon": session.surgeon,
                "phase": "pre_op",
            },
        ))

        session.agents_active = True
        print(f"[SESSION] Pre-op started: {session_id}")

        return {
            "status": "pre_op_started",
            "session_id": session_id,
            "agents_active": len(orch.agents),
        }

    # ── Phase 3: Intra-Op (Surgery Active) ────────────────

    async def start_intraop(self, session_id: str) -> dict:
        """
        Start intra-operative phase:
          - Vision pipeline starts (Holoscan or fallback)
          - Audio pipeline starts (ASR + TTS)
          - All agents fully active
          - Real-time event streaming begins
        """
        session = self._sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}

        session.phase = SessionPhase.INTRA_OP
        session.start_time = time.time()
        session.phase_history.append({"phase": "intra_op", "at": time.time()})

        # Start vision pipeline
        try:
            vis_orch = get_vision_orchestrator()
            vis_orch.set_event_callback(
                lambda event: get_orchestrator().dispatch(event)
            )
            await vis_orch.start(session_id)
            session.vision_active = True
        except Exception as e:
            print(f"[SESSION] Vision startup error: {e}")
            session.vision_active = False

        # Start camera health monitoring
        try:
            cam_mgr = get_camera_manager()
            await cam_mgr.start_health_monitor()
        except Exception as e:
            print(f"[SESSION] Camera health monitor error: {e}")

        session.audio_active = True  # ASR/TTS always available (browser fallback)

        # Dispatch intra-op start event
        orch = get_orchestrator()
        await orch.dispatch(AgentEvent(
            type=EventType.PHASE_CHANGE,
            source="session_manager",
            session_id=session_id,
            priority=3,
            data={"phase": "preparation", "at": time.time()},
        ))

        print(f"[SESSION] Intra-op started: {session_id} — Vision: {session.vision_active}")

        return {
            "status": "intra_op_started",
            "session_id": session_id,
            "vision_active": session.vision_active,
            "audio_active": session.audio_active,
        }

    # ── Phase 4: End Surgery ──────────────────────────────

    async def end_surgery(self, session_id: str) -> dict:
        """
        End the surgery and transition to post-op:
          - Chronicler generates final report
          - Vision pipeline stops
          - Session data archived
        """
        session = self._sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}

        session.phase = SessionPhase.POST_OP
        session.end_time = time.time()
        session.phase_history.append({"phase": "post_op", "at": time.time()})

        # Stop vision pipeline
        try:
            vis_orch = get_vision_orchestrator()
            await vis_orch.stop()
            session.vision_active = False
        except Exception:
            pass

        # Dispatch session end — Chronicler will generate report
        orch = get_orchestrator()
        await orch.end_session(session_id)
        session.agents_active = False

        duration_min = (session.end_time - session.start_time) / 60 if session.start_time else 0

        print(f"[SESSION] Surgery ended: {session_id} — {duration_min:.1f} min")

        return {
            "status": "post_op",
            "session_id": session_id,
            "duration_minutes": round(duration_min, 1),
            "phase_history": session.phase_history,
        }

    # ── Phase 5: Close ────────────────────────────────────

    async def close_session(self, session_id: str):
        """Close and archive the session."""
        session = self._sessions.get(session_id)
        if session:
            session.phase = SessionPhase.CLOSED
            session.phase_history.append({"phase": "closed", "at": time.time()})
            # TODO: Archive to Supabase / MinIO
            print(f"[SESSION] Closed: {session_id}")

    # ── WebSocket Broadcasting ────────────────────────────

    def register_ws_callback(self, session_id: str, callback):
        if session_id not in self._ws_callbacks:
            self._ws_callbacks[session_id] = []
        self._ws_callbacks[session_id].append(callback)

    def unregister_ws_callback(self, session_id: str, callback):
        if session_id in self._ws_callbacks:
            self._ws_callbacks[session_id] = [
                cb for cb in self._ws_callbacks[session_id] if cb != callback
            ]

    async def _broadcast_event(self, session_id: str, event: AgentEvent):
        """Broadcast an agent event to all WebSocket connections for this session."""
        callbacks = self._ws_callbacks.get(session_id, [])
        for cb in callbacks:
            try:
                await cb(event)
            except Exception as e:
                print(f"WS broadcast error: {e}")


# Singleton
_manager: Optional[SessionManager] = None


def get_session_manager() -> SessionManager:
    global _manager
    if _manager is None:
        _manager = SessionManager()
    return _manager
