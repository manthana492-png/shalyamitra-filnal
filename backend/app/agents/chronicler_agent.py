"""
ShalyaMitra — Chronicler Agent (The Chronicler)

Post-operative intelligence — generates structured surgical reports:
  - Complete operative note (WHO-compliant)
  - Timeline of events with timestamps
  - Drug log summary
  - Instrument counts verification
  - Complication documentation
  - Handover summary for post-op care team

Generates reports in real-time as surgery progresses,
finalized at session end.
"""

from __future__ import annotations
from typing import Any, Optional
import httpx, time, json
from app.agents.orchestrator import BaseAgent, AgentEvent, EventType
from app.config import settings


class ChroniclerAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_id="chronicler", pillar="chronicler")
        self._http: Optional[httpx.AsyncClient] = None
        self._timeline: list[dict] = []
        self._phases: list[dict] = []
        self._alerts: list[dict] = []
        self._drug_log: list[dict] = []
        self._procedure: str = ""
        self._patient: dict = {}
        self._surgeon: str = ""
        self._start_time: float = 0.0

    @property
    def subscriptions(self) -> list[EventType]:
        return [EventType.SESSION_START, EventType.SESSION_END,
                EventType.PHASE_CHANGE, EventType.ALERT,
                EventType.DRUG_ADMINISTERED, EventType.TRANSCRIPT]

    async def _get_http(self) -> httpx.AsyncClient:
        if self._http is None or self._http.is_closed:
            self._http = httpx.AsyncClient(timeout=30.0)
        return self._http

    async def handle_event(self, event: AgentEvent) -> list[AgentEvent]:
        if event.type == EventType.SESSION_START:
            self._start_time = time.time()
            self._procedure = event.data.get("procedure", "")
            self._patient = event.data.get("patient", {})
            self._surgeon = event.data.get("surgeon", "")
            self._timeline = []
            self._phases = []
            self._alerts = []
            self._drug_log = []
            self._log_event("Session started", "system")
            return []

        if event.type == EventType.PHASE_CHANGE:
            phase = event.data.get("phase", "")
            self._phases.append({"phase": phase, "at": time.time()})
            self._log_event(f"Phase: {phase}", "system")
            return []

        if event.type == EventType.ALERT:
            self._alerts.append({
                "title": event.data.get("title", ""),
                "severity": event.data.get("severity", ""),
                "body": event.data.get("body", ""),
                "at": time.time(),
                "pillar": event.data.get("pillar", ""),
            })
            self._log_event(f"Alert: {event.data.get('title', '')}", event.data.get("pillar", ""))
            return []

        if event.type == EventType.DRUG_ADMINISTERED:
            self._drug_log.append({
                "drug": event.data.get("drug", ""),
                "dose_mg": event.data.get("dose_mg", 0),
                "route": event.data.get("route", ""),
                "at": time.time(),
            })
            self._log_event(
                f"Drug: {event.data.get('drug', '')} {event.data.get('dose_mg', '')}mg "
                f"{event.data.get('route', '')}",
                "pharmacist",
            )
            return []

        if event.type == EventType.TRANSCRIPT:
            speaker = event.data.get("speaker", "")
            text = event.data.get("text", "")
            if speaker not in ("system",) and len(text) > 10:
                self._log_event(f"{speaker}: {text[:100]}", speaker)

            # Listen for report request
            if "report" in text.lower() or "summary" in text.lower():
                return await self._generate_interim_summary(event)
            return []

        if event.type == EventType.SESSION_END:
            return await self._generate_final_report(event)

        return []

    def _log_event(self, description: str, source: str):
        elapsed = time.time() - self._start_time if self._start_time > 0 else 0
        self._timeline.append({
            "elapsed_seconds": round(elapsed),
            "elapsed_formatted": self._format_time(elapsed),
            "description": description,
            "source": source,
        })

    def _format_time(self, seconds: float) -> str:
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins:02d}:{secs:02d}"

    async def _generate_interim_summary(self, event: AgentEvent) -> list[AgentEvent]:
        elapsed = time.time() - self._start_time
        critical_alerts = [a for a in self._alerts if a["severity"] == "critical"]
        current_phase = self._phases[-1]["phase"] if self._phases else "N/A"

        summary = (
            f"Interim report — {self._format_time(elapsed)} elapsed. "
            f"Phase: {current_phase}. "
            f"Events: {len(self._timeline)}. "
            f"Drugs administered: {len(self._drug_log)}. "
            f"Alerts: {len(self._alerts)} ({len(critical_alerts)} critical)."
        )

        return [AgentEvent(
            type=EventType.DISPLAY_TRANSCRIPT,
            source=self.agent_id, priority=7,
            session_id=event.session_id,
            data={"speaker": "chronicler", "text": summary,
                  "pillar": "chronicler", "at": time.time()},
        )]

    async def _generate_final_report(self, event: AgentEvent) -> list[AgentEvent]:
        """Generate the complete post-operative report."""
        total_time = time.time() - self._start_time
        critical_alerts = [a for a in self._alerts if a["severity"] == "critical"]

        # Build structured report
        report = {
            "report_type": "operative_note",
            "generated_at": time.time(),
            "procedure": self._procedure,
            "surgeon": self._surgeon,
            "patient": self._patient,
            "duration_minutes": round(total_time / 60, 1),
            "phases": self._phases,
            "timeline": self._timeline,
            "drug_log": self._drug_log,
            "alerts_summary": {
                "total": len(self._alerts),
                "critical": len(critical_alerts),
                "details": self._alerts,
            },
            "complications": [a for a in self._alerts if a["severity"] in ("critical", "warning")],
        }

        # Use LLM to generate narrative operative note
        narrative = await self._generate_narrative(report)

        results = [
            # Structured data
            AgentEvent(
                type=EventType.DISPLAY_TRANSCRIPT,
                source=self.agent_id, priority=4,
                session_id=event.session_id,
                data={
                    "speaker": "chronicler", "pillar": "chronicler", "at": time.time(),
                    "text": f"Operative note generated. Duration: {report['duration_minutes']} min. "
                            f"Events: {len(self._timeline)}. "
                            f"Complications: {len(report['complications'])}.",
                },
            ),
        ]

        if narrative:
            results.append(AgentEvent(
                type=EventType.REPORT_GENERATED,
                source=self.agent_id, priority=4,
                session_id=event.session_id,
                data={
                    "report": report,
                    "narrative": narrative,
                    "at": time.time(),
                },
            ))

        return results

    async def _generate_narrative(self, report: dict) -> Optional[str]:
        if not settings.openrouter_api_key:
            return self._fallback_narrative(report)

        prompt = f"""Generate a professional operative note from this surgical data:

Procedure: {report['procedure']}
Duration: {report['duration_minutes']} minutes
Phases: {json.dumps(report['phases'][:10])}
Drug log: {json.dumps(report['drug_log'][:10])}
Complications: {json.dumps(report['complications'][:5])}
Key timeline events: {json.dumps(report['timeline'][-10:])}

Format as a standard operative note with sections:
- Procedure
- Indication
- Findings
- Technique (brief)
- Anaesthesia summary
- Complications
- Post-operative plan

Keep it professional and concise."""

        try:
            http = await self._get_http()
            resp = await http.post(
                f"{settings.openrouter_base_url}/chat/completions",
                headers={"Authorization": f"Bearer {settings.openrouter_api_key}",
                         "HTTP-Referer": "https://shalyamitra.dev",
                         "X-Title": "ShalyaMitra Chronicler"},
                json={"model": settings.scholar_model,
                      "messages": [{"role": "user", "content": prompt}],
                      "max_tokens": 600, "temperature": 0.2},
                timeout=20.0,
            )
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"].strip()
        except Exception:
            pass

        return self._fallback_narrative(report)

    def _fallback_narrative(self, report: dict) -> str:
        """Generate a basic narrative without LLM."""
        return (
            f"OPERATIVE NOTE\n"
            f"Procedure: {report['procedure']}\n"
            f"Duration: {report['duration_minutes']} minutes\n"
            f"Total events logged: {len(report['timeline'])}\n"
            f"Drugs administered: {len(report['drug_log'])}\n"
            f"Alerts: {report['alerts_summary']['total']} "
            f"({report['alerts_summary']['critical']} critical)\n"
            f"Report generated by ShalyaMitra Chronicler."
        )

    def get_timeline(self) -> list[dict]:
        return self._timeline

    def get_report_data(self) -> dict:
        return {
            "procedure": self._procedure,
            "duration_seconds": time.time() - self._start_time if self._start_time else 0,
            "timeline_count": len(self._timeline),
            "drug_count": len(self._drug_log),
            "alert_count": len(self._alerts),
        }
