"""
ShalyaMitra — Eye Agent (Surgeon's Eye)

Surgical field analysis intelligence:
  - Anatomy identification and labelling
  - Surgical phase recognition
  - Retraction time monitoring (tissue damage prevention)
  - Critical View of Safety (CVS) verification for cholecystectomy
  - Anatomy overlay triggers

Uses: Camera 3 (surgeon's POV) vision data.
"""

from __future__ import annotations
from typing import Any
import time
from app.agents.orchestrator import BaseAgent, AgentEvent, EventType


class EyeAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_id="eye", pillar="eye")
        self._current_phase: str = "preparation"
        self._retraction_start: float = 0.0
        self._retraction_active: bool = False
        self._retraction_limit_minutes: float = 15.0
        self._retraction_warned: bool = False
        self._cvs_achieved: bool = False
        self._procedure: str = ""
        self._anatomy_seen: set[str] = set()

    @property
    def subscriptions(self) -> list[EventType]:
        return [EventType.SESSION_START, EventType.PHASE_CHANGE,
                EventType.ANATOMY_DETECTED, EventType.TRANSCRIPT]

    async def handle_event(self, event: AgentEvent) -> list[AgentEvent]:
        if event.type == EventType.SESSION_START:
            self._procedure = event.data.get("procedure", "")
            self._cvs_achieved = False
            self._anatomy_seen = set()
            return []

        if event.type == EventType.PHASE_CHANGE:
            return await self._on_phase_change(event)

        if event.type == EventType.ANATOMY_DETECTED:
            return await self._on_anatomy(event)

        if event.type == EventType.TRANSCRIPT:
            text = event.data.get("text", "").lower()
            if "retract" in text:
                return await self._handle_retraction(event)
            if "release" in text or "let go" in text:
                return await self._release_retraction(event)
            if "overlay" in text or "anatomy" in text:
                return await self._toggle_overlay(event)
        return []

    async def _on_phase_change(self, event: AgentEvent) -> list[AgentEvent]:
        old_phase = self._current_phase
        self._current_phase = event.data.get("phase", "")
        results: list[AgentEvent] = []

        # Announce phase transition
        results.append(AgentEvent(
            type=EventType.DISPLAY_TRANSCRIPT,
            source=self.agent_id, priority=6,
            session_id=event.session_id,
            data={
                "speaker": "eye", "pillar": "eye", "at": time.time(),
                "text": f"Phase transition: {old_phase} -> {self._current_phase}.",
            },
        ))

        # Check for CVS during cholecystectomy
        if ("cholecystectomy" in self._procedure.lower() and
                self._current_phase == "critical_step" and not self._cvs_achieved):
            results.append(AgentEvent(
                type=EventType.ALERT,
                source=self.agent_id, priority=3,
                session_id=event.session_id,
                data={
                    "title": "Critical View of Safety Required",
                    "body": "CVS not yet confirmed. Ensure 2 structures (cystic duct + artery) "
                            "clearly visible entering gallbladder before clipping.",
                    "severity": "warning", "pillar": "eye", "at": time.time(),
                },
            ))

        return results

    async def _on_anatomy(self, event: AgentEvent) -> list[AgentEvent]:
        labels = event.data.get("labels", [])
        results: list[AgentEvent] = []

        for label in labels:
            self._anatomy_seen.add(label.lower())

        # CVS check for cholecystectomy
        if "cholecystectomy" in self._procedure.lower() and not self._cvs_achieved:
            cvs_structures = {"cystic duct", "cystic artery"}
            if cvs_structures.issubset(self._anatomy_seen):
                self._cvs_achieved = True
                results.append(AgentEvent(
                    type=EventType.DISPLAY_TRANSCRIPT,
                    source=self.agent_id, priority=4,
                    session_id=event.session_id,
                    data={
                        "speaker": "eye", "pillar": "eye", "at": time.time(),
                        "text": "Critical View of Safety ACHIEVED. "
                                "Cystic duct and cystic artery clearly identified. "
                                "Safe to proceed with clipping.",
                    },
                ))

        return results

    async def _handle_retraction(self, event: AgentEvent) -> list[AgentEvent]:
        if not self._retraction_active:
            self._retraction_active = True
            self._retraction_start = time.time()
            self._retraction_warned = False
            return [AgentEvent(
                type=EventType.DISPLAY_TRANSCRIPT,
                source=self.agent_id, priority=7,
                session_id=event.session_id,
                data={
                    "speaker": "eye", "pillar": "eye", "at": time.time(),
                    "text": f"Retraction timer started. Limit: {self._retraction_limit_minutes} minutes.",
                },
            )]

        # Check if retraction time exceeded
        elapsed_min = (time.time() - self._retraction_start) / 60.0
        if elapsed_min >= self._retraction_limit_minutes and not self._retraction_warned:
            self._retraction_warned = True
            return [AgentEvent(
                type=EventType.ALERT,
                source=self.agent_id, priority=2,
                session_id=event.session_id,
                data={
                    "title": "Retraction Time Limit Reached",
                    "body": f"Retractor has been applied for {elapsed_min:.0f} minutes. "
                            f"Consider releasing to prevent tissue ischaemia.",
                    "severity": "warning", "pillar": "eye", "at": time.time(),
                },
            )]
        return []

    async def _release_retraction(self, event: AgentEvent) -> list[AgentEvent]:
        if self._retraction_active:
            elapsed_min = (time.time() - self._retraction_start) / 60.0
            self._retraction_active = False
            return [AgentEvent(
                type=EventType.DISPLAY_TRANSCRIPT,
                source=self.agent_id, priority=7,
                session_id=event.session_id,
                data={
                    "speaker": "eye", "pillar": "eye", "at": time.time(),
                    "text": f"Retraction released after {elapsed_min:.1f} minutes.",
                },
            )]
        return []

    async def _toggle_overlay(self, event: AgentEvent) -> list[AgentEvent]:
        return [AgentEvent(
            type=EventType.DISPLAY_VISION,
            source=self.agent_id, priority=6,
            session_id=event.session_id,
            data={
                "action": "toggle_overlay",
                "anatomy_seen": list(self._anatomy_seen),
                "at": time.time(),
            },
        )]
