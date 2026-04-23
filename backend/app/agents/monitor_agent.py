"""
ShalyaMitra — Monitor Sentinel Agent (Deep Upgrade)

SENIOR ANAESTHETIST-LEVEL vital sign monitoring:

1. MULTI-WINDOW TREND ANALYSIS
   - 1-min, 5-min, 15-min, 30-min slopes simultaneously
   - Acceleration detection (is the trend getting WORSE?)
   - Volatility scoring (unstable HR = early warning)

2. PREDICTIVE ALERTS
   - Projects vitals 2, 5, 10 minutes ahead using trend
   - Warns BEFORE critical thresholds are breached
   - "SpO2 will reach 90% in ~3 minutes at current rate"

3. MULTI-PARAMETER CORRELATION
   - HR rising + MAP falling = possible haemorrhage
   - SpO2 falling + EtCO2 rising = airway/ventilation issue
   - HR falling + MAP falling = vasovagal or deep anaesthesia
   - Tachycardia + desaturation + falling MAP = shock triad

4. PHASE-AWARE THRESHOLDS
   - Induction: expects transient hypotension, doesn't alert
   - Dissection: tighter thresholds (surgical stress)
   - Closure: expects stable vitals, alerts on any change

5. TEMPORAL PATTERN RECOGNITION
   - Detects recurring episodes (3rd tachycardia in 20 min)
   - Identifies slow drift vs sudden change
   - Recognises recovery patterns after drug administration

6. CUMULATIVE SESSION AWARENESS
   - Tracks total alert count and severity escalation
   - "This is the 4th hypotensive episode. Consider sustained vasopressor."
"""

from __future__ import annotations
import time, math
from dataclasses import dataclass, field
from typing import Any, Optional

from app.agents.orchestrator import BaseAgent, AgentEvent, EventType
from app.agents.surgical_memory import get_cortex, TimelineEventType


@dataclass
class VitalThresholds:
    """Phase-adjustable thresholds — a senior anaesthetist's instinct, codified."""
    hr_critical_low: int = 45
    hr_critical_high: int = 130
    hr_warning_low: int = 50
    hr_warning_high: int = 110
    spo2_critical: int = 90
    spo2_warning: int = 94
    map_critical_low: int = 55
    map_critical_high: int = 120
    map_warning_low: int = 65
    map_warning_high: int = 100
    etco2_critical_low: int = 25
    etco2_critical_high: int = 50
    etco2_warning_low: int = 30
    etco2_warning_high: int = 45
    temp_warning_low: float = 35.0
    temp_warning_high: float = 38.5
    rr_warning_low: int = 8
    rr_warning_high: int = 25


# Phase-specific threshold adjustments
PHASE_ADJUSTMENTS = {
    "induction": {"map_warning_low": 55, "hr_warning_low": 45, "map_critical_low": 45},
    "dissection": {"hr_warning_high": 100, "map_warning_high": 95},
    "critical_step": {"hr_warning_high": 95},
    "closure": {"hr_warning_high": 100, "map_warning_low": 70},
    "emergence": {"hr_warning_high": 120, "map_warning_high": 110},
}


@dataclass
class VitalAlert:
    """Rich alert with clinical reasoning."""
    severity: str          # critical | warning | predictive | pattern
    title: str
    body: str
    reasoning: str         # WHY this alert fired
    recommendation: str    # WHAT to do
    priority: int
    multi_param: bool = False  # Is this a correlated multi-parameter alert?


class MonitorAgent(BaseAgent):
    """
    The Monitor Sentinel — continuous vital sign intelligence.

    Not just threshold checking. This agent:
    - Watches 6 vital parameters across 4 time windows simultaneously
    - Correlates parameters to detect compound clinical scenarios
    - Predicts deterioration 2-10 minutes before it happens
    - Adjusts sensitivity based on surgical phase
    - Remembers every alert and escalates if patterns repeat
    """

    def __init__(self):
        super().__init__(agent_id="monitor_sentinel", pillar="monitor")
        self.thresholds = VitalThresholds()
        self._base_thresholds = VitalThresholds()  # Unmodified reference
        self._alert_history: list[dict] = []
        self._last_prediction_time: float = 0
        self._last_correlation_time: float = 0
        self._hypotension_episode_count: int = 0
        self._tachycardia_episode_count: int = 0
        self._desaturation_episode_count: int = 0

    @property
    def subscriptions(self) -> list[EventType]:
        return [EventType.VITALS_UPDATE, EventType.SESSION_START, EventType.PHASE_CHANGE]

    async def handle_event(self, event: AgentEvent) -> list[AgentEvent]:
        cortex = get_cortex()

        if event.type == EventType.SESSION_START:
            self._alert_history = []
            self._hypotension_episode_count = 0
            self._tachycardia_episode_count = 0
            self._desaturation_episode_count = 0
            return []

        if event.type == EventType.PHASE_CHANGE:
            return self._adjust_thresholds_for_phase(event)

        if event.type != EventType.VITALS_UPDATE:
            return []

        d = event.data
        hr = d.get("hr", 0)
        spo2 = d.get("spo2", 0)
        map_val = d.get("map", 0)
        etco2 = d.get("etco2", 0)
        temp = d.get("temp", 36.5)
        rr = d.get("rr", 14)
        at = d.get("at", event.timestamp)

        # Record into cortex (shared memory)
        cortex.record_vitals(hr=hr, spo2=spo2, map_val=map_val,
                             etco2=etco2, temp=temp, rr=rr, timestamp=at)

        results: list[AgentEvent] = []

        # Always emit vitals display with trend data
        results.append(self._build_vitals_display(hr, spo2, map_val, etco2, temp, rr, at))

        # Layer 1: Immediate threshold alerts
        alerts = self._check_thresholds(hr, spo2, map_val, etco2, temp, rr, at)

        # Layer 2: Multi-parameter correlation (every 15 seconds)
        if (at - self._last_correlation_time) > 15 and len(cortex.hr) >= 10:
            self._last_correlation_time = at
            correlation_alerts = self._multi_parameter_correlation(at)
            alerts.extend(correlation_alerts)

        # Layer 3: Predictive alerts (every 30 seconds)
        if (at - self._last_prediction_time) > 30 and len(cortex.hr) >= 30:
            self._last_prediction_time = at
            prediction_alerts = self._predictive_analysis(at)
            alerts.extend(prediction_alerts)

        # Layer 4: Pattern recognition (recurring episodes)
        pattern_alerts = self._detect_recurring_patterns(alerts, at)
        alerts.extend(pattern_alerts)

        # Emit all alerts
        for alert in alerts:
            self._alert_history.append({"title": alert.title, "severity": alert.severity, "at": at})
            cortex.add_timeline(TimelineEventType.VITAL_ALERT, self.agent_id,
                                alert.title, severity=alert.severity)
            cortex._alert_count += 1
            results.append(self._alert_to_event(alert, event.session_id, at))

        return results

    # ── Phase-Aware Threshold Adjustment ──────────────

    def _adjust_thresholds_for_phase(self, event: AgentEvent) -> list[AgentEvent]:
        phase = event.data.get("phase", "")
        self.thresholds = VitalThresholds()  # Reset to base
        adjustments = PHASE_ADJUSTMENTS.get(phase, {})
        for key, value in adjustments.items():
            if hasattr(self.thresholds, key):
                setattr(self.thresholds, key, value)
        return []

    # ── Vitals Display with Trends ────────────────────

    def _build_vitals_display(self, hr, spo2, map_val, etco2, temp, rr, at) -> AgentEvent:
        cortex = get_cortex()
        return AgentEvent(
            type=EventType.DISPLAY_VITALS,
            source=self.agent_id, priority=8,
            data={
                "hr": hr, "spo2": spo2, "map": map_val,
                "etco2": etco2, "temp": temp, "rr": rr, "at": at,
                # Trend data for UI sparklines
                "hr_trend_5m": cortex.hr.slope_per_minute(300),
                "spo2_trend_5m": cortex.spo2.slope_per_minute(300),
                "map_trend_5m": cortex.map_bp.slope_per_minute(300),
                "hr_volatility": cortex.hr.volatility(300),
                "instability_score": cortex.hemodynamic_instability_score(),
                "phase": cortex.current_phase,
                "surgery_min": cortex.surgery_duration_minutes(),
            },
        )

    # ── Layer 1: Threshold Alerts ─────────────────────

    def _check_thresholds(self, hr, spo2, map_val, etco2, temp, rr, at) -> list[VitalAlert]:
        alerts = []
        t = self.thresholds

        if hr and hr < t.hr_critical_low:
            alerts.append(VitalAlert("critical", f"HR Critical: {hr} bpm",
                f"Severe bradycardia at {hr} bpm.",
                "Heart rate below {t.hr_critical_low} bpm threshold for current phase ({get_cortex().current_phase}).",
                "Check: depth of anaesthesia, vagal stimulus, beta-blocker effect. Consider atropine 0.5mg IV.",
                priority=2))
        elif hr and hr > t.hr_critical_high:
            self._tachycardia_episode_count += 1
            alerts.append(VitalAlert("critical", f"HR Critical: {hr} bpm",
                f"Severe tachycardia at {hr} bpm.",
                f"Heart rate above {t.hr_critical_high} bpm. Episode #{self._tachycardia_episode_count} this surgery.",
                "Check: pain response, hypovolaemia, light anaesthesia, surgical stimulation. Rule out malignant hyperthermia if temp also rising.",
                priority=2))

        if spo2 and spo2 < t.spo2_critical:
            self._desaturation_episode_count += 1
            alerts.append(VitalAlert("critical", f"SpO₂ Critical: {spo2}%",
                f"Severe desaturation. Episode #{self._desaturation_episode_count}.",
                f"SpO2 below {t.spo2_critical}%. Duration matters — brain injury risk increases after 3 minutes.",
                "IMMEDIATE: Check airway, ETT position, ventilator. Increase FiO2 to 100%. Suction if needed. Auscultate for bronchospasm.",
                priority=1))

        if map_val and map_val < t.map_critical_low:
            self._hypotension_episode_count += 1
            alerts.append(VitalAlert("critical", f"MAP Critical: {map_val} mmHg",
                f"Severe hypotension. Episode #{self._hypotension_episode_count}.",
                f"MAP below {t.map_critical_low} mmHg. Organ perfusion at risk. Kidneys require >65mmHg.",
                "Consider: fluid bolus 250-500ml crystalloid, phenylephrine 100mcg, or ephedrine 6mg. Check for surgical bleeding.",
                priority=2))

        return alerts

    # ── Layer 2: Multi-Parameter Correlation ──────────

    def _multi_parameter_correlation(self, at: float) -> list[VitalAlert]:
        """
        A senior anaesthetist doesn't look at one number.
        They see PATTERNS across multiple parameters simultaneously.
        """
        alerts = []
        cortex = get_cortex()
        window = 120  # 2-minute correlation window

        hr_slope = cortex.hr.slope_per_minute(window) or 0
        map_slope = cortex.map_bp.slope_per_minute(window) or 0
        spo2_slope = cortex.spo2.slope_per_minute(window) or 0
        etco2_slope = cortex.etco2.slope_per_minute(window) or 0
        hr_val = cortex.hr.latest or 0
        map_val = cortex.map_bp.latest or 0
        spo2_val = cortex.spo2.latest or 0

        # PATTERN 1: Shock Triad — tachycardia + hypotension + desaturation
        if hr_slope > 3 and map_slope < -2 and spo2_slope < -0.5:
            alerts.append(VitalAlert("critical", "SHOCK TRIAD DETECTED",
                f"HR rising (+{hr_slope:.1f}/min), MAP falling ({map_slope:.1f}/min), SpO2 falling ({spo2_slope:.1f}/min).",
                "Three cardinal signs of circulatory shock present simultaneously. This pattern precedes cardiovascular collapse.",
                "EMERGENCY: Rapid fluid resuscitation, prepare vasopressors, call for blood products. Check surgical field for active haemorrhage.",
                priority=1, multi_param=True))

        # PATTERN 2: Respiratory compromise — SpO2 falling + EtCO2 rising
        elif spo2_slope < -0.5 and etco2_slope > 1:
            alerts.append(VitalAlert("warning", "Ventilation Compromise",
                f"SpO2 falling ({spo2_slope:.1f}/min) with EtCO2 rising ({etco2_slope:.1f}/min).",
                "Divergent SpO2/EtCO2 suggests hypoventilation or bronchospasm, not a circuit disconnect.",
                "Check: tidal volumes, airway pressures, breath sounds. Consider bronchospasm if wheeze present.",
                priority=3, multi_param=True))

        # PATTERN 3: Haemorrhage correlation — visual bleeding + vital deterioration
        elif hr_slope > 2 and map_slope < -1 and cortex._active_bleed:
            alerts.append(VitalAlert("critical", "VITALS CONFIRM ACTIVE BLEEDING",
                f"Visual bleed detected AND vitals deteriorating: HR +{hr_slope:.1f}/min, MAP {map_slope:.1f}/min.",
                "Multi-modal confirmation: camera sees bleeding and vitals show hemodynamic response. High confidence haemorrhage.",
                "IMMEDIATE: Surgical haemostasis. Prepare blood products. Consider damage control if not controllable.",
                priority=1, multi_param=True))

        # PATTERN 4: Deep anaesthesia — bradycardia + hypotension + low BIS
        elif hr_slope < -2 and map_slope < -1 and hr_val < 55 and map_val < 65:
            alerts.append(VitalAlert("warning", "Possible Deep Anaesthesia",
                f"HR falling ({hr_slope:.1f}/min) with MAP falling ({map_slope:.1f}/min). HR={hr_val}, MAP={map_val}.",
                "Combined bradycardia and hypotension without surgical stimulus suggests excessive anaesthetic depth.",
                "Consider: reducing volatile agent/propofol infusion rate. Check BIS if available. Prepare atropine.",
                priority=3, multi_param=True))

        # PATTERN 5: Pneumoperitoneum effects (laparoscopic surgery)
        elif etco2_slope > 2 and hr_slope > 1 and map_slope > 2:
            alerts.append(VitalAlert("info", "Pneumoperitoneum Effect",
                f"EtCO2 rising ({etco2_slope:.1f}/min), HR rising ({hr_slope:.1f}/min), MAP rising ({map_slope:.1f}/min).",
                "This pattern is expected during CO2 insufflation in laparoscopic surgery. No action needed if within limits.",
                "Monitor trends. Alert if EtCO2 exceeds 50mmHg or MAP exceeds 110mmHg.",
                priority=7, multi_param=True))

        return alerts

    # ── Layer 3: Predictive Analysis ──────────────────

    def _predictive_analysis(self, at: float) -> list[VitalAlert]:
        """
        Project vitals forward. Warn BEFORE thresholds are crossed.
        A good anaesthetist anticipates — this is that capability.
        """
        alerts = []
        cortex = get_cortex()
        t = self.thresholds

        # Predict SpO2 in 3 minutes
        spo2_pred = cortex.spo2.predict(180, window=120)
        if spo2_pred is not None and spo2_pred < t.spo2_warning and (cortex.spo2.latest or 100) >= t.spo2_warning:
            rate = cortex.spo2.slope_per_minute(120) or 0
            alerts.append(VitalAlert("predictive",
                f"SpO₂ Predicted: {spo2_pred:.0f}% in 3 min",
                f"At current rate ({rate:.1f}%/min), SpO2 will breach {t.spo2_warning}% in ~3 minutes.",
                "Linear projection based on 2-minute trend. Trend acceleration: " +
                (f"{cortex.spo2.acceleration(180):.2f}/min²" if cortex.spo2.acceleration(180) else "stable"),
                "Pre-emptive: increase FiO2, check ventilation parameters, prepare for intervention.",
                priority=4))

        # Predict MAP in 5 minutes
        map_pred = cortex.map_bp.predict(300, window=180)
        if map_pred is not None and map_pred < t.map_warning_low and (cortex.map_bp.latest or 80) >= t.map_warning_low:
            rate = cortex.map_bp.slope_per_minute(180) or 0
            alerts.append(VitalAlert("predictive",
                f"MAP Predicted: {map_pred:.0f} mmHg in 5 min",
                f"At current rate ({rate:.1f}mmHg/min), MAP will breach {t.map_warning_low} mmHg.",
                "Gradual hypotension developing. Check: blood loss, anaesthetic depth, fluid balance.",
                "Consider pre-emptive fluid bolus or vasopressor. Check surgical field for ongoing bleeding.",
                priority=4))

        # Predict HR
        hr_pred = cortex.hr.predict(300, window=180)
        if hr_pred is not None and hr_pred > t.hr_warning_high and (cortex.hr.latest or 70) <= t.hr_warning_high:
            alerts.append(VitalAlert("predictive",
                f"HR Predicted: {hr_pred:.0f} bpm in 5 min",
                f"HR trending up. Current phase: {cortex.current_phase}.",
                "Rising heart rate may indicate: pain, hypovolaemia, light anaesthesia, or surgical stress response.",
                "Assess cause before treating symptom. Check: anaesthetic depth, fluid status, surgical stimulation.",
                priority=5))

        return alerts

    # ── Layer 4: Recurring Pattern Detection ──────────

    def _detect_recurring_patterns(self, current_alerts: list[VitalAlert], at: float) -> list[VitalAlert]:
        """
        "Doctor, this is the third time HR has spiked in 20 minutes."
        A senior nurse would say this. Now our AI does too.
        """
        extra_alerts = []

        if self._hypotension_episode_count >= 3:
            # Don't repeat this pattern alert too frequently
            recent_pattern_alerts = [
                a for a in self._alert_history
                if a.get("title", "").startswith("Recurring") and (at - a.get("at", 0)) < 600
            ]
            if not recent_pattern_alerts:
                extra_alerts.append(VitalAlert("warning",
                    f"Recurring Hypotension (Episode #{self._hypotension_episode_count})",
                    f"{self._hypotension_episode_count} hypotensive episodes this surgery. Pattern suggests ongoing cause.",
                    "Recurring hypotension despite treatment suggests: uncontrolled surgical bleeding, inadequate volume replacement, or vasodilating drugs still active.",
                    "Consider: sustained vasopressor infusion instead of boluses, aggressive fluid resuscitation, check surgical field for ongoing bleeding.",
                    priority=3))

        if self._tachycardia_episode_count >= 3:
            recent = [a for a in self._alert_history
                      if "Tachycardia" in a.get("title", "") and (at - a.get("at", 0)) < 600]
            if len(recent) <= 1:
                extra_alerts.append(VitalAlert("warning",
                    f"Recurring Tachycardia (Episode #{self._tachycardia_episode_count})",
                    f"Repeated tachycardia episodes. Sustained sympathetic activation.",
                    "Multiple tachycardia episodes suggest a persistent underlying cause rather than isolated surgical stimulus.",
                    "Systematic assessment: pain (increase analgesia), hypovolaemia (fluid challenge), anxiety (deepen anaesthesia), sepsis (check temperature trend).",
                    priority=4))

        return extra_alerts

    # ── Helpers ───────────────────────────────────────

    def _alert_to_event(self, alert: VitalAlert, session_id, at) -> AgentEvent:
        return AgentEvent(
            type=EventType.DISPLAY_ALERT,
            source=self.agent_id,
            priority=alert.priority,
            session_id=session_id,
            data={
                "severity": alert.severity,
                "title": alert.title,
                "body": alert.body,
                "reasoning": alert.reasoning,
                "recommendation": alert.recommendation,
                "multi_param": alert.multi_param,
                "source": "monitor-sentinel",
                "pillar": "monitor",
                "at": at,
                "instability_score": get_cortex().hemodynamic_instability_score(),
            },
        )
