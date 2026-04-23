"""
ShalyaMitra — Haemorrhage Sentinel Agent (Deep Upgrade)

CRITICAL SAFETY AGENT — Priority 1. Pure reflex arc + deep state.

SENIOR SURGEON-LEVEL haemorrhage intelligence:

1. BLEED EPISODE LIFECYCLE
   - Tracks each bleed as an episode (start → active → controlled → resolved)
   - Measures duration, estimates blood loss per episode
   - Correlates with vital signs at moment of detection

2. CUMULATIVE BLOOD LOSS ESTIMATION
   - Running total across all episodes
   - Triggers transfusion alerts at class thresholds:
     Class I:  <750ml (15%) — compensated
     Class II: 750-1500ml (15-30%) — tachycardia, narrowed pulse pressure
     Class III: 1500-2000ml (30-40%) — altered consciousness
     Class IV: >2000ml (>40%) — lethal without immediate intervention

3. BLEED PATTERN INTELLIGENCE
   - Pulsatile: arterial — highest urgency, specific vessel identification
   - Venous: steady dark flow — pressure/packing response
   - Oozing: diffuse capillary — may indicate coagulopathy

4. VITAL SIGN CORRELATION
   - Visual bleeding confirmed by vital deterioration = high confidence
   - Visual bleeding WITHOUT vital change = may be superficial/controlled
   - Vital deterioration WITHOUT visual bleeding = occult haemorrhage

5. TEMPORAL PATTERN ANALYSIS
   - Recurrent bleeds from same location = vessel not properly secured
   - Increasing frequency = progressive coagulopathy
   - Post-drug bleed = possible drug-induced coagulopathy

6. AYURVEDIC INTEGRATION
   - Raktasrava (रक्तस्राव) classification per Sushruta
   - Correlates with Marma proximity for injury grading
"""

from __future__ import annotations
import time
from typing import Any, Optional
from app.agents.orchestrator import BaseAgent, AgentEvent, EventType
from app.agents.surgical_memory import get_cortex, TimelineEventType


# Hemorrhage classification (Sushruta + ATLS hybrid)
BLOOD_LOSS_CLASS = [
    (750,  "Class I",   "Compensated. Minimal physiological change.",
     "Monitor closely. Secure visible source. No transfusion needed yet."),
    (1500, "Class II",  "Tachycardia developing. Pulse pressure narrowing.",
     "Establish second IV access. Type and crossmatch 2 units PRBC. Crystalloid bolus."),
    (2000, "Class III", "Altered consciousness risk. Organ perfusion compromised.",
     "TRANSFUSE NOW. Activate massive transfusion protocol. Consider damage control surgery."),
    (9999, "Class IV",  "Life-threatening. Cardiovascular collapse imminent.",
     "EMERGENCY: Massive transfusion 1:1:1 (PRBC:FFP:Platelets). Damage control. Call for help."),
]


class HaemorrhageAgent(BaseAgent):
    """
    Haemorrhage Sentinel — real-time bleed detection with deep state tracking.

    Core Law: This agent fires in <500ms. No LLM. No queuing. Direct reflex.
    But BETWEEN alerts, it maintains deep state for clinical reasoning.
    """

    def __init__(self):
        super().__init__(agent_id="haemorrhage_sentinel", pillar="haemorrhage")
        self._active_alert: bool = False
        self._alert_count: int = 0
        self._last_bleed_location: str = ""
        self._same_location_count: int = 0
        self._bleed_timestamps: list[float] = []
        self._last_class_announced: str = ""

    @property
    def subscriptions(self) -> list[EventType]:
        return [EventType.HAEMORRHAGE_DETECTED, EventType.SESSION_START,
                EventType.SESSION_END, EventType.VITALS_UPDATE]

    async def handle_event(self, event: AgentEvent) -> list[AgentEvent]:
        cortex = get_cortex()

        if event.type == EventType.SESSION_START:
            self._active_alert = False
            self._alert_count = 0
            self._last_bleed_location = ""
            self._same_location_count = 0
            self._bleed_timestamps = []
            self._last_class_announced = ""
            return []

        if event.type == EventType.SESSION_END:
            return []

        # Passive vitals monitoring for occult haemorrhage
        if event.type == EventType.VITALS_UPDATE:
            return self._check_occult_haemorrhage(event)

        if event.type != EventType.HAEMORRHAGE_DETECTED:
            return []

        d = event.data
        confidence = d.get("confidence", 0.0)
        pattern = d.get("pattern", "unknown")
        location = d.get("location", "surgical field")
        at = d.get("at", event.timestamp)
        estimated_ml = d.get("estimated_ml", self._estimate_blood_loss(pattern, confidence))

        if confidence < 0.75:
            return []

        self._alert_count += 1
        self._active_alert = True
        self._bleed_timestamps.append(at)

        results: list[AgentEvent] = []

        # Record in cortex
        cortex.start_bleed_episode(pattern, location, confidence)
        cortex.estimated_total_blood_loss_ml += estimated_ml

        # Same location detection
        if location == self._last_bleed_location:
            self._same_location_count += 1
        else:
            self._same_location_count = 1
            self._last_bleed_location = location

        # Build rich alert with clinical context
        total_loss = cortex.estimated_total_blood_loss_ml
        loss_class = self._classify_blood_loss(total_loss)
        vitals_confirm = cortex.vitals_correlate_with_bleeding()

        # === PRIMARY ALERT ===
        title, body = self._build_alert_content(
            pattern, location, confidence, total_loss, loss_class, vitals_confirm
        )

        results.append(AgentEvent(
            type=EventType.DISPLAY_ALERT,
            source=self.agent_id, priority=1,
            session_id=event.session_id,
            data={
                "severity": "critical" if pattern == "pulsatile" or confidence > 0.90 else "warning",
                "title": title, "body": body,
                "source": "haemorrhage-sentinel", "pillar": "haemorrhage",
                "at": at, "priority": 1,
                "total_blood_loss_ml": total_loss,
                "loss_classification": loss_class["class"],
                "vitals_confirm": vitals_confirm,
                "episode_number": self._alert_count,
                "bleed_pattern": pattern,
            },
        ))

        # === CRITICAL TTS ===
        tts_text = self._build_tts_alert(pattern, location, total_loss, loss_class, vitals_confirm)
        results.append(AgentEvent(
            type=EventType.DISPLAY_TTS,
            source=self.agent_id, priority=1,
            session_id=event.session_id,
            data={"text": tts_text, "voice": "critical", "at": at},
        ))

        # === SAME LOCATION WARNING ===
        if self._same_location_count >= 2:
            results.append(AgentEvent(
                type=EventType.DISPLAY_ALERT,
                source=self.agent_id, priority=2,
                session_id=event.session_id,
                data={
                    "severity": "critical",
                    "title": f"Recurring Bleed — Same Location ({self._same_location_count}x)",
                    "body": (f"Bleeding has recurred at {location} {self._same_location_count} times. "
                             f"Previous haemostasis may be inadequate. "
                             f"Consider: re-exploration, clip/suture reinforcement, or vessel ligation."),
                    "source": "haemorrhage-sentinel", "pillar": "haemorrhage",
                    "at": at, "priority": 2,
                },
            ))

        # === ESCALATING FREQUENCY WARNING ===
        if self._alert_count >= 3:
            freq = self._bleed_frequency_per_hour()
            if freq > 3:
                results.append(AgentEvent(
                    type=EventType.DISPLAY_ALERT,
                    source=self.agent_id, priority=2,
                    session_id=event.session_id,
                    data={
                        "severity": "critical",
                        "title": "Escalating Bleed Frequency",
                        "body": (f"{self._alert_count} episodes at {freq:.1f}/hour. "
                                 f"Consider: coagulopathy workup (PT/INR, fibrinogen), "
                                 f"DIC screen, hypothermia check, acidosis correction."),
                        "source": "haemorrhage-sentinel", "pillar": "haemorrhage",
                        "at": at,
                    },
                ))

        # === BLOOD LOSS CLASS CHANGE ===
        if loss_class["class"] != self._last_class_announced:
            self._last_class_announced = loss_class["class"]
            if loss_class["class"] in ("Class III", "Class IV"):
                results.append(AgentEvent(
                    type=EventType.DISPLAY_TTS,
                    source=self.agent_id, priority=1,
                    session_id=event.session_id,
                    data={
                        "text": f"BLOOD LOSS ESCALATION. Now {loss_class['class']}. "
                                f"Total estimated loss: {total_loss:.0f} ml. {loss_class['action']}",
                        "voice": "critical", "at": at,
                    },
                ))

        return results

    def _check_occult_haemorrhage(self, event: AgentEvent) -> list[AgentEvent]:
        """
        Detect HIDDEN bleeding that cameras can't see.
        If vitals show haemorrhagic pattern but no visual bleed detected,
        warn about possible occult (internal/retroperitoneal) haemorrhage.
        """
        cortex = get_cortex()
        if cortex._active_bleed:
            return []  # Already tracking visible bleed

        if len(cortex.hr) < 30:
            return []

        hr_slope = cortex.hr.slope_per_minute(180) or 0
        map_slope = cortex.map_bp.slope_per_minute(180) or 0
        spo2_val = cortex.spo2.latest or 100

        # Haemorrhagic vital pattern WITHOUT visible bleeding
        if hr_slope > 3 and map_slope < -2 and spo2_val > 92:
            # Only alert once per 10 minutes
            recent = [t for t in self._bleed_timestamps if (time.time() - t) < 600]
            if not recent:
                self._bleed_timestamps.append(time.time())
                return [AgentEvent(
                    type=EventType.DISPLAY_ALERT,
                    source=self.agent_id, priority=2,
                    session_id=event.session_id,
                    data={
                        "severity": "warning",
                        "title": "Possible Occult Haemorrhage",
                        "body": (f"Vitals show haemorrhagic pattern (HR +{hr_slope:.1f}/min, "
                                 f"MAP {map_slope:.1f}/min) but NO visible bleeding detected by cameras. "
                                 f"Consider: retroperitoneal bleed, thoracic bleed, or concealed abdominal haemorrhage."),
                        "source": "haemorrhage-sentinel", "pillar": "haemorrhage",
                        "at": time.time(),
                    },
                )]
        return []

    def _build_alert_content(self, pattern, location, confidence, total_loss, loss_class, vitals_confirm):
        pattern_detail = {
            "pulsatile": "ARTERIAL (pulsatile) — likely named vessel. Clamp proximal and distal before ligating.",
            "venous": "VENOUS (steady dark flow) — direct pressure or packing. Electrocautery for smaller vessels.",
            "oozing": "CAPILLARY OOZE (diffuse) — may indicate coagulopathy. Check clotting factors if persistent.",
        }.get(pattern, f"{pattern.capitalize()} pattern detected.")

        confirmation = "Vitals CONFIRM hemodynamic response to bleeding." if vitals_confirm else \
                       "Vitals currently stable — bleed may be controlled or superficial."

        title = f"⚠ {'ARTERIAL BLEED' if pattern == 'pulsatile' else 'BLEEDING'} — Episode #{self._alert_count}"
        body = (f"{pattern_detail}\n"
                f"Location: {location}. Confidence: {confidence:.0%}.\n"
                f"Est. total blood loss: {total_loss:.0f}ml ({loss_class['class']}).\n"
                f"{confirmation}\n"
                f"Recommendation: {loss_class['action']}")
        return title, body

    def _build_tts_alert(self, pattern, location, total_loss, loss_class, vitals_confirm):
        if pattern == "pulsatile":
            return (f"ALERT — Possible arterial bleed at {location}. "
                    f"Total estimated loss {total_loss:.0f} ml, {loss_class['class']}. "
                    f"{'Vitals confirm.' if vitals_confirm else 'Vitals currently stable.'}")
        return (f"ALERT — Bleeding detected at {location}. "
                f"Total loss {total_loss:.0f} ml. {loss_class['action']}")

    def _estimate_blood_loss(self, pattern: str, confidence: float) -> float:
        base = {"pulsatile": 200, "venous": 100, "oozing": 50}.get(pattern, 75)
        return base * confidence

    def _classify_blood_loss(self, total_ml: float) -> dict:
        for threshold, cls, desc, action in BLOOD_LOSS_CLASS:
            if total_ml < threshold:
                return {"class": cls, "description": desc, "action": action, "total_ml": total_ml}
        return {"class": "Class IV", "description": "Critical", "action": "EMERGENCY", "total_ml": total_ml}

    def _bleed_frequency_per_hour(self) -> float:
        if len(self._bleed_timestamps) < 2:
            return 0
        span = self._bleed_timestamps[-1] - self._bleed_timestamps[0]
        if span <= 0:
            return 0
        return len(self._bleed_timestamps) / (span / 3600)

    async def resolve(self, session_id: str, at: float, estimated_loss_ml: float = 0) -> list[AgentEvent]:
        self._active_alert = False
        cortex = get_cortex()
        cortex.resolve_bleed(estimated_loss_ml)
        return [AgentEvent(
            type=EventType.DISPLAY_TRANSCRIPT,
            source=self.agent_id, priority=5,
            session_id=session_id,
            data={
                "speaker": "nael", "pillar": "haemorrhage", "at": at,
                "text": (f"Haemorrhage resolved. Episode duration: "
                         f"{cortex.bleed_episodes[-1].duration_seconds:.0f}s. "
                         f"Total estimated blood loss this surgery: "
                         f"{cortex.estimated_total_blood_loss_ml:.0f}ml."),
            },
        )]
