"""
ShalyaMitra — Agent Orchestrator (ShalyaBus)

The central surgical event bus that coordinates all 11 intelligence agents.
Each agent subscribes to specific event types and publishes results.

NOTE: This is ShalyaMitra's CUSTOM orchestrator — distinct from the
OpenClaw agentic OS framework. In production, this runs INSIDE an
NVIDIA NemoClaw sandbox for enterprise security, privacy routing,
and agent isolation.

Architecture:
  - Agents register with ShalyaBus at startup
  - Events flow through Redis Pub/Sub channels (or in-memory for demo)
  - Each agent has persistent memory (Redis hash) per session
  - The Critical Alert Path bypasses the bus entirely (hardwired <50ms)
  - NemoClaw wraps each agent in an OpenShell sandbox for isolation

Event flow:
  Holoscan (vision) ──→ [ShalyaBus] ──→ Display (frontend)
  Riva (audio)      ──→ [ShalyaBus] ──→ NIM (reasoning) → TTS → Display
  NIM (reasoning)   ──→ [ShalyaBus] ──→ Display

Priority routing:
  Priority 1-2: Critical → immediate dispatch, no queuing
  Priority 3-5: Urgent  → next available slot
  Priority 6-8: Normal  → queued, may be batched
"""

from __future__ import annotations

import asyncio
import json
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional
from uuid import uuid4

import orjson


# ── Event Types ───────────────────────────────────────────

class EventType(str, Enum):
    # Vision events (from Holoscan)
    VITALS_UPDATE = "vitals_update"
    INSTRUMENT_DETECTED = "instrument_detected"
    ANATOMY_DETECTED = "anatomy_detected"
    HAEMORRHAGE_DETECTED = "haemorrhage_detected"
    PHASE_CHANGE = "phase_change"
    RETRACTION_STARTED = "retraction_started"
    RETRACTION_THRESHOLD = "retraction_threshold"

    # Audio events (from Riva)
    TRANSCRIPT = "transcript"
    WAKE_WORD = "wake_word"
    SPEAKER_IDENTIFIED = "speaker_identified"

    # Reasoning events (from NIM / agents)
    ALERT = "alert"
    KNOWLEDGE_RESULT = "knowledge_result"
    ADVOCATE_CHALLENGE = "advocate_challenge"
    DRUG_LOG = "drug_log"
    DRUG_ADMINISTERED = "drug_administered"
    PK_UPDATE = "pk_update"
    REPORT_GENERATED = "report_generated"

    # Display events (to frontend)
    DISPLAY_TRANSCRIPT = "display_transcript"
    DISPLAY_ALERT = "display_alert"
    DISPLAY_VITALS = "display_vitals"
    DISPLAY_PHASE = "display_phase"
    DISPLAY_VISION = "display_vision"
    DISPLAY_OVERLAY = "display_overlay"
    DISPLAY_KNOWLEDGE = "display_knowledge"
    DISPLAY_TTS = "display_tts"

    # Lifecycle
    SESSION_START = "session_start"
    SESSION_END = "session_end"
    AGENT_READY = "agent_ready"


@dataclass
class AgentEvent:
    """An event flowing through the orchestrator bus."""
    id: str = field(default_factory=lambda: str(uuid4()))
    type: EventType = EventType.TRANSCRIPT
    source: str = "system"           # Which agent/service produced this
    priority: int = 8                # 1=critical, 8=background
    timestamp: float = field(default_factory=time.time)
    session_id: Optional[str] = None
    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.type.value,
            "source": self.source,
            "priority": self.priority,
            "timestamp": self.timestamp,
            "session_id": self.session_id,
            "data": self.data,
        }


# ── Agent Base Class ──────────────────────────────────────

class BaseAgent(ABC):
    """
    Base class for all ShalyaMitra intelligence agents.

    Each agent:
      - Has a unique ID and pillar association
      - Subscribes to specific event types
      - Publishes results back to the orchestrator
      - Has per-session persistent memory
    """

    def __init__(self, agent_id: str, pillar: str):
        self.agent_id = agent_id
        self.pillar = pillar
        self._orchestrator: Optional[AgentOrchestrator] = None
        self._memory: dict[str, Any] = {}

    @property
    @abstractmethod
    def subscriptions(self) -> list[EventType]:
        """Event types this agent listens to."""
        ...

    @abstractmethod
    async def handle_event(self, event: AgentEvent) -> list[AgentEvent]:
        """
        Process an incoming event and return zero or more response events.

        Returns:
            List of events to publish (may be empty).
        """
        ...

    async def publish(self, event: AgentEvent):
        """Publish an event to the orchestrator bus."""
        if self._orchestrator:
            await self._orchestrator.dispatch(event)

    async def on_session_start(self, session_id: str):
        """Called when a surgery session begins."""
        self._memory = {}

    async def on_session_end(self, session_id: str):
        """Called when a surgery session ends."""
        pass


# ── Orchestrator ──────────────────────────────────────────

class AgentOrchestrator:
    """
    Central event bus for all agents.

    In production, this uses Redis Pub/Sub for distribution.
    In local/demo mode, it uses in-memory asyncio queues.
    """

    def __init__(self):
        self.agents: dict[str, BaseAgent] = {}
        self._subscriptions: dict[EventType, list[BaseAgent]] = {}
        self._event_log: list[AgentEvent] = []
        self._display_callback: Optional[Callable] = None

    def register_agent(self, agent: BaseAgent):
        """Register an agent with the orchestrator."""
        agent._orchestrator = self
        self.agents[agent.agent_id] = agent
        for event_type in agent.subscriptions:
            if event_type not in self._subscriptions:
                self._subscriptions[event_type] = []
            self._subscriptions[event_type].append(agent)

    def set_display_callback(self, callback: Callable):
        """Set the callback for sending events to the frontend display."""
        self._display_callback = callback

    async def dispatch(self, event: AgentEvent):
        """
        Dispatch an event to all subscribed agents.

        Critical priority events (1-2) are dispatched immediately.
        Normal events are dispatched in order.
        """
        self._event_log.append(event)

        # If this is a display event, forward to frontend
        if event.type.value.startswith("display_") and self._display_callback:
            await self._display_callback(event)
            return

        # Find subscribed agents
        subscribers = self._subscriptions.get(event.type, [])

        if event.priority <= 2:
            # CRITICAL — dispatch to all subscribers concurrently
            tasks = [agent.handle_event(event) for agent in subscribers]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, list):
                    for response_event in result:
                        await self.dispatch(response_event)
        else:
            # Normal priority — sequential dispatch
            for agent in subscribers:
                try:
                    responses = await agent.handle_event(event)
                    for response_event in responses:
                        await self.dispatch(response_event)
                except Exception as e:
                    print(f"Agent {agent.agent_id} error: {e}")

    async def start_session(self, session_id: str, procedure: str = "",
                            weight_kg: float = 70.0, age: int = 50):
        """Initialize all agents and the Surgical Memory Cortex."""
        from app.agents.surgical_memory import get_cortex, reset_cortex
        reset_cortex()
        cortex = get_cortex()
        cortex.start_session(session_id, procedure, weight_kg, age)
        for agent in self.agents.values():
            await agent.on_session_start(session_id)
        await self.dispatch(AgentEvent(
            type=EventType.SESSION_START,
            source="orchestrator",
            session_id=session_id,
            priority=1,
            data={"procedure": procedure, "patient": {"weight_kg": weight_kg, "age": age}},
        ))

    async def end_session(self, session_id: str):
        """Finalize all agents and generate session summary from cortex."""
        await self.dispatch(AgentEvent(
            type=EventType.SESSION_END,
            source="orchestrator",
            session_id=session_id,
            priority=1,
        ))
        for agent in self.agents.values():
            await agent.on_session_end(session_id)
        # Generate session summary from cortex
        from app.agents.surgical_memory import get_cortex
        return get_cortex().end_session()

    def get_event_log(self) -> list[dict]:
        """Get the full event log for this session."""
        return [e.to_dict() for e in self._event_log]


# ── Singleton ─────────────────────────────────────────────
_orchestrator: Optional[AgentOrchestrator] = None


def get_orchestrator(register_all: bool = True) -> AgentOrchestrator:
    """Get the global agent orchestrator with all 11 agents registered."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AgentOrchestrator()
        if register_all:
            _register_all_agents(_orchestrator)
    return _orchestrator


def _register_all_agents(orch: AgentOrchestrator):
    """Register all 11 intelligence pillar agents."""
    from app.agents.voice_agent import VoiceAgent
    from app.agents.monitor_agent import MonitorAgent
    from app.agents.haemorrhage_agent import HaemorrhageAgent
    from app.agents.sentinel_agent import SentinelAgent
    from app.agents.eye_agent import EyeAgent
    from app.agents.scholar_agent import ScholarAgent
    from app.agents.pharmacist_agent import PharmacistAgent
    from app.agents.oracle_agent import OracleAgent
    from app.agents.consultant_agent import ConsultantAgent
    from app.agents.devils_advocate_agent import DevilsAdvocateAgent
    from app.agents.chronicler_agent import ChroniclerAgent

    agents = [
        VoiceAgent(),           # Pillar 1: The Voice (Nael)
        MonitorAgent(),         # Pillar 2: Monitor Sentinel
        HaemorrhageAgent(),     # Pillar 3: Haemorrhage Sentinel
        SentinelAgent(),        # Pillar 4: The Sentinel (instruments)
        EyeAgent(),             # Pillar 5: Surgeon's Eye
        ScholarAgent(),         # Pillar 6: The Scholar
        PharmacistAgent(),      # Pillar 7: The Pharmacist
        OracleAgent(),          # Pillar 8: The Oracle
        ConsultantAgent(),      # Pillar 9: The Consultant
        DevilsAdvocateAgent(),  # Pillar 10: Devil's Advocate
        ChroniclerAgent(),      # Pillar 11: The Chronicler
    ]

    for agent in agents:
        orch.register_agent(agent)

    print(f"[AGENTS] Registered {len(agents)} intelligence pillars")
