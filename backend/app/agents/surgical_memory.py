"""
ShalyaMitra — Surgical Memory Cortex

The temporal, cross-modal, phase-aware shared memory system for all agents.
This is what makes ShalyaMitra's agents STATEFUL across a 4-hour surgery.

Architecture:
  ┌─────────────────────────────────────────────────┐
  │              Surgical Memory Cortex              │
  ├─────────────┬──────────┬────────────┬───────────┤
  │ Vitals Ring │ Timeline │ Drug State │ Vision    │
  │ Buffer      │ Events   │ Machine    │ History   │
  ├─────────────┼──────────┼────────────┼───────────┤
  │ 60-min      │ Full     │ PK decay   │ Phase     │
  │ sliding     │ surgery  │ curves     │ + anatomy │
  │ window      │ timeline │ per drug   │ memory    │
  └─────────────┴──────────┴────────────┴───────────┘

Capabilities:
  1. TREND ANALYSIS — slope, acceleration, volatility over 1/5/15/30/60 min
  2. MULTI-PARAMETER CORRELATION — vitals dropping + bleeding = compound alert
  3. PHASE AWARENESS — what's normal in dissection is alarming in closure
  4. TEMPORAL PATTERNS — was there a similar episode 20 minutes ago?
  5. CUMULATIVE TRACKING — total blood loss, total drugs, total events
  6. CLINICAL CONTEXT — builds a running patient narrative for LLM queries
  7. CROSS-AGENT QUERIES — "what was HR doing when Cam3 saw bleeding?"
"""

from __future__ import annotations
import time, math, statistics
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


# ═══════════════════════════════════════════════════════
# Time-Series Ring Buffer
# ═══════════════════════════════════════════════════════

@dataclass
class TimestampedValue:
    value: float
    timestamp: float


class TimeSeriesBuffer:
    """Fixed-capacity ring buffer with time-windowed analysis."""

    def __init__(self, max_duration_seconds: int = 3600):
        self._data: deque[TimestampedValue] = deque()
        self._max_duration = max_duration_seconds

    def add(self, value: float, timestamp: Optional[float] = None):
        ts = timestamp or time.time()
        self._data.append(TimestampedValue(value, ts))
        # Evict old entries
        cutoff = ts - self._max_duration
        while self._data and self._data[0].timestamp < cutoff:
            self._data.popleft()

    def window(self, seconds: int) -> list[TimestampedValue]:
        """Get values from the last N seconds."""
        if not self._data:
            return []
        cutoff = self._data[-1].timestamp - seconds
        return [d for d in self._data if d.timestamp >= cutoff]

    def values_in_window(self, seconds: int) -> list[float]:
        return [d.value for d in self.window(seconds)]

    @property
    def latest(self) -> Optional[float]:
        return self._data[-1].value if self._data else None

    @property
    def latest_timestamp(self) -> Optional[float]:
        return self._data[-1].timestamp if self._data else None

    def __len__(self) -> int:
        return len(self._data)

    # ── Statistical Analysis ──────────────────────────

    def mean(self, seconds: int = 60) -> Optional[float]:
        vals = self.values_in_window(seconds)
        return statistics.mean(vals) if vals else None

    def stdev(self, seconds: int = 60) -> Optional[float]:
        vals = self.values_in_window(seconds)
        return statistics.stdev(vals) if len(vals) >= 2 else None

    def slope(self, seconds: int = 60) -> Optional[float]:
        """Linear regression slope (change per second)."""
        data = self.window(seconds)
        if len(data) < 3:
            return None
        n = len(data)
        t0 = data[0].timestamp
        xs = [d.timestamp - t0 for d in data]
        ys = [d.value for d in data]
        x_mean = sum(xs) / n
        y_mean = sum(ys) / n
        num = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
        den = sum((x - x_mean) ** 2 for x in xs)
        return num / den if den != 0 else 0.0

    def slope_per_minute(self, seconds: int = 60) -> Optional[float]:
        s = self.slope(seconds)
        return s * 60 if s is not None else None

    def acceleration(self, seconds: int = 120) -> Optional[float]:
        """Rate of change of slope (is the trend accelerating?)."""
        half = seconds // 2
        s1 = self.slope(half)  # Recent half
        data = self.window(seconds)
        if len(data) < 6:
            return None
        # Slope of older half
        mid_time = data[len(data) // 2].timestamp
        older = [d for d in data if d.timestamp < mid_time]
        if len(older) < 3:
            return None
        n = len(older)
        t0 = older[0].timestamp
        xs = [d.timestamp - t0 for d in older]
        ys = [d.value for d in older]
        x_mean = sum(xs) / n
        y_mean = sum(ys) / n
        num = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
        den = sum((x - x_mean) ** 2 for x in xs)
        s0 = num / den if den != 0 else 0.0
        return (s1 - s0) if s1 is not None else None

    def volatility(self, seconds: int = 60) -> Optional[float]:
        """Coefficient of variation — how unstable is this parameter?"""
        m = self.mean(seconds)
        s = self.stdev(seconds)
        if m and s and m != 0:
            return abs(s / m)
        return None

    def min_max(self, seconds: int = 60) -> tuple[Optional[float], Optional[float]]:
        vals = self.values_in_window(seconds)
        return (min(vals), max(vals)) if vals else (None, None)

    def predict(self, seconds_ahead: int, window: int = 120) -> Optional[float]:
        """Predict value N seconds in the future using linear trend."""
        s = self.slope(window)
        if s is None or self.latest is None:
            return None
        return self.latest + s * seconds_ahead

    def deviation_from_baseline(self, baseline_window: int = 300) -> Optional[float]:
        """How far is current value from the 5-min baseline mean?"""
        baseline = self.mean(baseline_window)
        if baseline is None or self.latest is None:
            return None
        return self.latest - baseline


# ═══════════════════════════════════════════════════════
# Surgical Phase State
# ═══════════════════════════════════════════════════════

class SurgicalPhase(str, Enum):
    PREPARATION = "preparation"
    INDUCTION = "induction"
    POSITIONING = "positioning"
    DRAPING = "draping"
    INCISION = "incision"
    DISSECTION = "dissection"
    CRITICAL_STEP = "critical_step"
    HAEMOSTASIS = "haemostasis"
    CLOSURE = "closure"
    EMERGENCE = "emergence"
    COMPLETE = "complete"


@dataclass
class PhaseRecord:
    phase: str
    entered_at: float
    exited_at: Optional[float] = None
    duration_seconds: Optional[float] = None
    events_during: int = 0
    alerts_during: int = 0


# ═══════════════════════════════════════════════════════
# Timeline Event
# ═══════════════════════════════════════════════════════

class TimelineEventType(str, Enum):
    VITAL_ALERT = "vital_alert"
    DRUG_GIVEN = "drug_given"
    INSTRUMENT_COUNT = "instrument_count"
    PHASE_CHANGE = "phase_change"
    HAEMORRHAGE = "haemorrhage"
    ANATOMY_NOTED = "anatomy_noted"
    SURGEON_STATEMENT = "surgeon_statement"
    AGENT_ALERT = "agent_alert"
    DEVILS_CHALLENGE = "devils_challenge"
    MARMA_ADVISORY = "marma_advisory"


@dataclass
class TimelineEvent:
    type: TimelineEventType
    timestamp: float
    source_agent: str
    summary: str
    data: dict[str, Any] = field(default_factory=dict)
    severity: str = "info"


# ═══════════════════════════════════════════════════════
# Drug State Tracking
# ═══════════════════════════════════════════════════════

@dataclass
class DrugDose:
    drug: str
    dose_mg: float
    dose_per_kg: float
    route: str
    timestamp: float
    # PK parameters
    onset_min: float = 1.0
    peak_min: float = 5.0
    duration_min: float = 30.0
    # Computed state
    is_active: bool = True


@dataclass
class DrugState:
    """Cumulative drug tracking for one drug over the surgery."""
    drug: str
    doses: list[DrugDose] = field(default_factory=list)
    total_mg: float = 0.0
    total_per_kg: float = 0.0
    last_dose_at: float = 0.0

    def add_dose(self, dose: DrugDose):
        self.doses.append(dose)
        self.total_mg += dose.dose_mg
        self.total_per_kg += dose.dose_per_kg
        self.last_dose_at = dose.timestamp

    def minutes_since_last(self) -> float:
        if not self.last_dose_at:
            return float("inf")
        return (time.time() - self.last_dose_at) / 60

    def is_any_active(self) -> bool:
        now = time.time()
        return any(
            (now - d.timestamp) / 60 < d.duration_min
            for d in self.doses
        )

    def estimated_plasma_level_pct(self) -> float:
        """Rough estimate of remaining plasma level (0-100%)."""
        now = time.time()
        total_effect = 0.0
        for d in self.doses:
            elapsed_min = (now - d.timestamp) / 60
            if elapsed_min < d.onset_min:
                total_effect += (elapsed_min / d.onset_min) * 100
            elif elapsed_min < d.peak_min:
                total_effect += 100
            elif elapsed_min < d.duration_min:
                decay_pct = 1 - (elapsed_min - d.peak_min) / (d.duration_min - d.peak_min)
                total_effect += max(0, decay_pct * 100)
        return min(100, total_effect)


# ═══════════════════════════════════════════════════════
# Haemorrhage Tracking
# ═══════════════════════════════════════════════════════

@dataclass
class BleedEpisode:
    detected_at: float
    resolved_at: Optional[float] = None
    pattern: str = "unknown"          # pulsatile, venous, oozing
    location: str = "surgical field"
    max_confidence: float = 0.0
    vitals_at_detection: dict = field(default_factory=dict)
    estimated_blood_loss_ml: float = 0.0
    duration_seconds: float = 0.0


# ═══════════════════════════════════════════════════════
# The Cortex — Shared Memory for All Agents
# ═══════════════════════════════════════════════════════

class SurgicalMemoryCortex:
    """
    The shared, time-aware, cross-modal memory system.
    One instance per surgery session. All 11 agents read and write.

    Usage:
        cortex = get_cortex()
        cortex.record_vitals(hr=72, spo2=98, ...)
        trend = cortex.hr.slope_per_minute(300)  # 5-min HR trend
        context = cortex.build_clinical_context()  # For LLM prompts
    """

    def __init__(self):
        self.session_id: Optional[str] = None
        self.started_at: float = 0.0
        self.procedure_name: str = ""
        self.patient_weight_kg: float = 70.0
        self.patient_age: int = 50

        # ── Vitals Time Series (60-min sliding window) ────
        self.hr = TimeSeriesBuffer(3600)
        self.spo2 = TimeSeriesBuffer(3600)
        self.map_bp = TimeSeriesBuffer(3600)
        self.etco2 = TimeSeriesBuffer(3600)
        self.temp = TimeSeriesBuffer(3600)
        self.rr = TimeSeriesBuffer(3600)
        self.systolic = TimeSeriesBuffer(3600)
        self.diastolic = TimeSeriesBuffer(3600)

        # ── Surgical Phase Tracking ───────────────────────
        self.current_phase: str = "preparation"
        self.phase_history: list[PhaseRecord] = []
        self._phase_entered_at: float = 0.0

        # ── Timeline (full surgery) ───────────────────────
        self.timeline: list[TimelineEvent] = []

        # ── Drug State Machine ────────────────────────────
        self.drugs: dict[str, DrugState] = {}

        # ── Haemorrhage Episodes ──────────────────────────
        self.bleed_episodes: list[BleedEpisode] = []
        self._active_bleed: Optional[BleedEpisode] = None
        self.estimated_total_blood_loss_ml: float = 0.0

        # ── Instrument State ──────────────────────────────
        self.instrument_baseline: dict[str, int] = {}
        self.instrument_current: dict[str, int] = {}
        self.instrument_snapshots: list[tuple[float, dict[str, int]]] = []

        # ── Anatomical Landmarks Seen ─────────────────────
        self.anatomy_seen: list[dict] = []  # {"structure", "confidence", "timestamp"}

        # ── Surgeon Decisions / Statements ────────────────
        self.surgeon_statements: list[dict] = []

        # ── Cross-Modal Correlation Counters ──────────────
        self._alert_count: int = 0
        self._challenge_count: int = 0

    # ── Vitals Recording ──────────────────────────────

    def record_vitals(self, hr=None, spo2=None, map_val=None,
                      etco2=None, temp=None, rr=None,
                      systolic=None, diastolic=None,
                      timestamp=None):
        ts = timestamp or time.time()
        if hr is not None: self.hr.add(hr, ts)
        if spo2 is not None: self.spo2.add(spo2, ts)
        if map_val is not None: self.map_bp.add(map_val, ts)
        if etco2 is not None: self.etco2.add(etco2, ts)
        if temp is not None: self.temp.add(temp, ts)
        if rr is not None: self.rr.add(rr, ts)
        if systolic is not None: self.systolic.add(systolic, ts)
        if diastolic is not None: self.diastolic.add(diastolic, ts)

    # ── Phase Management ──────────────────────────────

    def transition_phase(self, new_phase: str, timestamp: Optional[float] = None):
        ts = timestamp or time.time()
        if self.current_phase:
            self.phase_history.append(PhaseRecord(
                phase=self.current_phase,
                entered_at=self._phase_entered_at,
                exited_at=ts,
                duration_seconds=ts - self._phase_entered_at if self._phase_entered_at else 0,
            ))
        self.current_phase = new_phase
        self._phase_entered_at = ts
        self.add_timeline(TimelineEventType.PHASE_CHANGE, "system",
                          f"Phase → {new_phase}", timestamp=ts)

    def phase_duration_minutes(self) -> float:
        if not self._phase_entered_at:
            return 0.0
        return (time.time() - self._phase_entered_at) / 60

    def surgery_duration_minutes(self) -> float:
        if not self.started_at:
            return 0.0
        return (time.time() - self.started_at) / 60

    # ── Timeline ──────────────────────────────────────

    def add_timeline(self, event_type: TimelineEventType, source: str,
                     summary: str, severity: str = "info",
                     data: Optional[dict] = None, timestamp: Optional[float] = None):
        self.timeline.append(TimelineEvent(
            type=event_type,
            timestamp=timestamp or time.time(),
            source_agent=source,
            summary=summary,
            data=data or {},
            severity=severity,
        ))

    def recent_timeline(self, minutes: int = 5) -> list[TimelineEvent]:
        cutoff = time.time() - minutes * 60
        return [e for e in self.timeline if e.timestamp >= cutoff]

    # ── Drug Tracking ─────────────────────────────────

    def record_drug(self, drug: str, dose_mg: float, route: str = "IV",
                    onset_min=1.0, peak_min=5.0, duration_min=30.0):
        dose = DrugDose(
            drug=drug, dose_mg=dose_mg,
            dose_per_kg=round(dose_mg / self.patient_weight_kg, 2),
            route=route, timestamp=time.time(),
            onset_min=onset_min, peak_min=peak_min, duration_min=duration_min,
        )
        if drug not in self.drugs:
            self.drugs[drug] = DrugState(drug=drug)
        self.drugs[drug].add_dose(dose)
        self.add_timeline(TimelineEventType.DRUG_GIVEN, "pharmacist",
                          f"{drug} {dose_mg}mg {route}", data={"dose_per_kg": dose.dose_per_kg})

    def active_drugs(self) -> list[str]:
        return [name for name, state in self.drugs.items() if state.is_any_active()]

    def total_drug_dose(self, drug: str) -> float:
        return self.drugs[drug].total_mg if drug in self.drugs else 0.0

    # ── Haemorrhage Tracking ──────────────────────────

    def start_bleed_episode(self, pattern: str, location: str, confidence: float):
        vitals_snap = {
            "hr": self.hr.latest, "spo2": self.spo2.latest,
            "map": self.map_bp.latest, "etco2": self.etco2.latest,
        }
        episode = BleedEpisode(
            detected_at=time.time(), pattern=pattern,
            location=location, max_confidence=confidence,
            vitals_at_detection=vitals_snap,
        )
        self._active_bleed = episode
        self.bleed_episodes.append(episode)
        self.add_timeline(TimelineEventType.HAEMORRHAGE, "haemorrhage",
                          f"{pattern} bleed at {location} (conf {confidence:.0%})",
                          severity="critical")

    def resolve_bleed(self, estimated_loss_ml: float = 0.0):
        if self._active_bleed:
            self._active_bleed.resolved_at = time.time()
            self._active_bleed.duration_seconds = (
                self._active_bleed.resolved_at - self._active_bleed.detected_at
            )
            self._active_bleed.estimated_blood_loss_ml = estimated_loss_ml
            self.estimated_total_blood_loss_ml += estimated_loss_ml
            self._active_bleed = None

    # ── Multi-Parameter Correlation ───────────────────

    def hemodynamic_instability_score(self, window_seconds: int = 300) -> float:
        """
        0-100 score representing hemodynamic instability.
        Combines: HR volatility + MAP trend + SpO2 deviation + bleeding status.
        A senior anaesthetist watches these together — so does our AI.
        """
        score = 0.0

        # HR volatility (normal <5%, unstable >15%)
        hr_vol = self.hr.volatility(window_seconds)
        if hr_vol is not None:
            score += min(25, hr_vol * 250)

        # MAP falling trend (dropping >2mmHg/min is concerning)
        map_slope = self.map_bp.slope_per_minute(window_seconds)
        if map_slope is not None and map_slope < -1:
            score += min(25, abs(map_slope) * 10)

        # SpO2 deviation from baseline
        spo2_dev = self.spo2.deviation_from_baseline(window_seconds)
        if spo2_dev is not None and spo2_dev < -2:
            score += min(25, abs(spo2_dev) * 5)

        # Active bleeding
        if self._active_bleed:
            score += 25

        return min(100, score)

    def vitals_correlate_with_bleeding(self) -> bool:
        """Do vitals support the visual bleeding detection?"""
        hr_rising = (self.hr.slope_per_minute(120) or 0) > 2
        map_falling = (self.map_bp.slope_per_minute(120) or 0) < -2
        spo2_falling = (self.spo2.slope_per_minute(120) or 0) < -0.5
        return sum([hr_rising, map_falling, spo2_falling]) >= 2

    # ── Clinical Context Builder ──────────────────────

    def build_clinical_context(self, max_chars: int = 2000) -> str:
        """
        Build a rich clinical context string for LLM prompts.
        This is what makes agent responses CONTEXT-AWARE.
        """
        parts = []
        dur = self.surgery_duration_minutes()
        parts.append(f"Surgery: {self.procedure_name or 'Unknown'}, "
                     f"Duration: {dur:.0f}min, Phase: {self.current_phase} "
                     f"({self.phase_duration_minutes():.0f}min in phase)")

        # Current vitals with trends
        if self.hr.latest is not None:
            hr_trend = self.hr.slope_per_minute(300)
            trend_str = f", trend {hr_trend:+.1f}/min" if hr_trend else ""
            parts.append(f"HR: {self.hr.latest:.0f} bpm{trend_str}")
        if self.spo2.latest is not None:
            parts.append(f"SpO2: {self.spo2.latest:.0f}%")
        if self.map_bp.latest is not None:
            parts.append(f"MAP: {self.map_bp.latest:.0f} mmHg")

        # Hemodynamic stability
        instability = self.hemodynamic_instability_score()
        if instability > 20:
            parts.append(f"⚠ Hemodynamic instability: {instability:.0f}/100")

        # Active drugs
        active = self.active_drugs()
        if active:
            drug_strs = []
            for name in active:
                state = self.drugs[name]
                level = state.estimated_plasma_level_pct()
                drug_strs.append(f"{name} ({state.total_mg}mg total, ~{level:.0f}% plasma)")
            parts.append("Active drugs: " + ", ".join(drug_strs))

        # Blood loss
        if self.estimated_total_blood_loss_ml > 0:
            parts.append(f"Est. blood loss: {self.estimated_total_blood_loss_ml:.0f}ml")

        # Recent events
        recent = self.recent_timeline(5)
        if recent:
            event_strs = [f"[{e.severity}] {e.summary}" for e in recent[-5:]]
            parts.append("Recent: " + "; ".join(event_strs))

        # Instrument status
        if self.instrument_baseline:
            total_init = sum(self.instrument_baseline.values())
            total_curr = sum(self.instrument_current.values())
            parts.append(f"Instruments: {total_curr}/{total_init}")

        context = "\n".join(parts)
        return context[:max_chars]

    # ── Session Lifecycle ─────────────────────────────

    def start_session(self, session_id: str, procedure: str = "",
                      weight_kg: float = 70.0, age: int = 50):
        self.session_id = session_id
        self.started_at = time.time()
        self.procedure_name = procedure
        self.patient_weight_kg = weight_kg
        self.patient_age = age
        self.current_phase = "preparation"
        self._phase_entered_at = self.started_at

    def end_session(self) -> dict:
        """Generate session summary for Chronicler."""
        return {
            "session_id": self.session_id,
            "procedure": self.procedure_name,
            "duration_minutes": self.surgery_duration_minutes(),
            "phases": [{"phase": p.phase, "duration_min": (p.duration_seconds or 0) / 60}
                       for p in self.phase_history],
            "total_drugs": {name: state.total_mg for name, state in self.drugs.items()},
            "total_blood_loss_ml": self.estimated_total_blood_loss_ml,
            "bleed_episodes": len(self.bleed_episodes),
            "total_alerts": self._alert_count,
            "total_challenges": self._challenge_count,
            "timeline_events": len(self.timeline),
            "instruments_verified": bool(self.instrument_baseline),
        }


# ═══════════════════════════════════════════════════════
# Singleton
# ═══════════════════════════════════════════════════════

_cortex: Optional[SurgicalMemoryCortex] = None

def get_cortex() -> SurgicalMemoryCortex:
    global _cortex
    if _cortex is None:
        _cortex = SurgicalMemoryCortex()
    return _cortex

def reset_cortex():
    global _cortex
    _cortex = SurgicalMemoryCortex()
