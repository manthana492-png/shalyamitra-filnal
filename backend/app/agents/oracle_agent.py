"""
ShalyaMitra — Oracle Agent (The Oracle)

Ayurvedic surgical intelligence — provides Marma advisories,
Shloka references, and classical Sushruta Samhita context
mapped to modern surgical anatomy.

Uses: Marma DB + RAG over Shalyatantra corpus.
"""

from __future__ import annotations
from typing import Any, Optional
import time
from app.agents.orchestrator import BaseAgent, AgentEvent, EventType
from app.knowledge.marma_db import get_marma_for_procedure, get_marma_by_zone, MARMA_DB
from app.knowledge.rag_pipeline import RAGPipeline


class OracleAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_id="oracle", pillar="oracle")
        self._procedure: str = ""
        self._active_marma_zones: list[dict] = []

    @property
    def subscriptions(self) -> list[EventType]:
        return [EventType.SESSION_START, EventType.PHASE_CHANGE,
                EventType.TRANSCRIPT, EventType.ANATOMY_DETECTED]

    async def handle_event(self, event: AgentEvent) -> list[AgentEvent]:
        if event.type == EventType.SESSION_START:
            return await self._on_session_start(event)
        if event.type == EventType.PHASE_CHANGE:
            return await self._on_phase_change(event)
        if event.type == EventType.ANATOMY_DETECTED:
            return await self._on_anatomy(event)
        if event.type == EventType.TRANSCRIPT:
            text = event.data.get("text", "").lower()
            if any(kw in text for kw in ["oracle", "marma", "shloka", "sushruta",
                                          "ayurved", "shalyatantra", "classical"]):
                return await self._answer_query(event)
        return []

    async def _on_session_start(self, event: AgentEvent) -> list[AgentEvent]:
        self._procedure = event.data.get("procedure", "")
        self._active_marma_zones = get_marma_for_procedure(self._procedure)

        if self._active_marma_zones:
            zone_summary = ", ".join(m["name"] for m in self._active_marma_zones[:3])
            return [AgentEvent(
                type=EventType.DISPLAY_TRANSCRIPT,
                source=self.agent_id, priority=7,
                session_id=event.session_id,
                data={
                    "speaker": "oracle", "pillar": "oracle", "at": time.time(),
                    "text": f"Marma advisory loaded for {self._procedure}. "
                            f"Key zones: {zone_summary}. "
                            f"I will alert when dissection approaches these points.",
                },
            )]
        return []

    async def _on_phase_change(self, event: AgentEvent) -> list[AgentEvent]:
        phase = event.data.get("phase", "")
        results: list[AgentEvent] = []

        # During critical dissection phases, proactively advise on Marma zones
        if phase in ("dissection", "critical_step"):
            for marma in self._active_marma_zones:
                if marma.get("risk") in ("High", "Critical"):
                    shloka = marma.get("shloka", {})
                    shloka_text = shloka.get("transliteration", "") if shloka else ""
                    results.append(AgentEvent(
                        type=EventType.ALERT,
                        source=self.agent_id, priority=4,
                        session_id=event.session_id,
                        data={
                            "title": f"Marma Zone: {marma['name']}",
                            "body": (f"{marma.get('zone', '')} - {marma.get('note', '')}. "
                                    f"{shloka_text}"),
                            "severity": "caution",
                            "pillar": "oracle", "at": time.time(),
                        },
                    ))
        return results

    async def _on_anatomy(self, event: AgentEvent) -> list[AgentEvent]:
        """When vision detects anatomy, check for nearby Marma zones."""
        labels = event.data.get("labels", [])
        results: list[AgentEvent] = []

        for label in labels:
            matching = get_marma_by_zone(label)
            for marma in matching:
                results.append(AgentEvent(
                    type=EventType.DISPLAY_TRANSCRIPT,
                    source=self.agent_id, priority=7,
                    session_id=event.session_id,
                    data={
                        "speaker": "oracle", "pillar": "oracle", "at": time.time(),
                        "text": f"Marma proximity: {marma['name']} ({marma['devanagari']}) "
                                f"in {marma['zone']} — {marma.get('note', '')}",
                    },
                ))
        return results

    async def _answer_query(self, event: AgentEvent) -> list[AgentEvent]:
        query = event.data.get("text", "")
        rag = RAGPipeline()
        results = await rag.query(query, top_k=2)
        context = "\n".join(r.get("text", "") for r in results) if results else ""

        # Build response with Marma context
        marma_context = ""
        if self._active_marma_zones:
            marma_context = "\nActive Marma zones: " + "; ".join(
                f"{m['name']} ({m['zone']}, risk: {m['risk']})" for m in self._active_marma_zones
            )

        response = (f"Shalyatantra reference: {context[:200]}" if context
                    else "No specific Shalyatantra reference found for this query.")
        if marma_context:
            response += marma_context

        return [AgentEvent(
            type=EventType.DISPLAY_TRANSCRIPT,
            source=self.agent_id, priority=7,
            session_id=event.session_id,
            data={"speaker": "oracle", "text": response, "pillar": "oracle", "at": time.time()},
        )]
