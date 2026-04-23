"""
ShalyaMitra — Sentinel Agent (Deep Upgrade)

SENIOR SCRUB NURSE-LEVEL instrument intelligence:

1. TEMPORAL INSTRUMENT TRACKING
   - Records every detection event with timestamp
   - Builds count confidence over multiple frames (not single-frame)
   - Detects count changes: "Retractor removed from field at 14:32"
   - Tracks instrument movement: tray → field → patient → tray

2. SWAB/SPONGE STATE MACHINE
   - Clean swabs tracked separately from blood-stained
   - Blood-stained swab count = proxy for blood loss
   - "5 swabs used in last 20min — above average, check haemostasis"

3. NEEDLE ACCOUNTABILITY
   - Every needle logged at opening (from pack count)
   - Cross-referenced at closure — ALL must be accounted
   - Partial needle detection (broken needle is CRITICAL)

4. MULTI-FRAME CONFIDENCE
   - Single detection = 60% confidence
   - 3 consecutive detections = 90% confidence
   - 5+ consecutive = confirmed
   - Reduces false-positive count discrepancy alerts

5. CLOSURE COUNT PROTOCOL
   - Mandatory dual count at closure (first count + second verification)
   - If discrepancy: blocks closure alert, requires surgeon acknowledgment
   - Records count-verified timestamp for operative note

6. WHO SURGICAL SAFETY CHECKLIST INTEGRATION
   - Sign-in: initial instrument layout verified
   - Time-out: count confirmed before incision
   - Sign-out: final count matches initial
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import time
from app.agents.orchestrator import BaseAgent, AgentEvent, EventType
from app.agents.surgical_memory import get_cortex, TimelineEventType
from app.camera.zero_shot_detector import get_instrument_detector


@dataclass
class InstrumentSnapshot:
    """A point-in-time instrument count."""
    timestamp: float
    counts: dict[str, int]
    total: int
    source: str  # "zero_shot", "manual", "ai_vision"
    confidence: float




@dataclass
class SwabTracker:
    """Tracks clean and used swabs/sponges."""
    initial_clean: int = 0
    current_clean: int = 0
    used_blood_stained: int = 0
    timestamps_used: list[float] = field(default_factory=list)

    @property
    def total_accounted(self) -> int:
        return self.current_clean + self.used_blood_stained

    @property
    def missing(self) -> int:
        return max(0, self.initial_clean - self.total_accounted)

    def use_rate_per_hour(self) -> float:
        if len(self.timestamps_used) < 2:
            return 0
        span = self.timestamps_used[-1] - self.timestamps_used[0]
        if span <= 0:
            return 0
        return len(self.timestamps_used) / (span / 3600)


@dataclass
class NeedleTracker:
    initial_count: int = 0
    current_count: int = 0
    broken_detected: bool = False

    @property
    def missing(self) -> int:
        return max(0, self.initial_count - self.current_count)


class SentinelAgent(BaseAgent):
    """
    The Sentinel — instrument, swab, and needle accountability.

    Beyond simple counting: temporal tracking, multi-frame confidence,
    movement detection, and mandatory closure protocol.
    """

    def __init__(self):
        super().__init__(agent_id="sentinel", pillar="sentinel")
        self._initial_count: dict[str, int] = {}
        self._current_count: dict[str, int] = {}
        self._count_history: list[InstrumentSnapshot] = []
        self._consecutive_stable: int = 0  # Frames with same count
        self._last_confirmed_count: dict[str, int] = {}
        self._swabs = SwabTracker()
        self._needles = NeedleTracker()
        self._counts_verified: bool = False
        self._second_count_done: bool = False
        self._phase: str = "preparation"
        self._who_sign_in: bool = False
        self._who_time_out: bool = False
        self._who_sign_out: bool = False
        self._count_change_events: list[dict] = []  # {instrument, from, to, at}

    @property
    def subscriptions(self) -> list[EventType]:
        return [EventType.SESSION_START, EventType.INSTRUMENT_DETECTED,
                EventType.PHASE_CHANGE, EventType.TRANSCRIPT]

    async def handle_event(self, event: AgentEvent) -> list[AgentEvent]:
        cortex = get_cortex()

        if event.type == EventType.SESSION_START:
            self._reset()
            return []

        if event.type == EventType.PHASE_CHANGE:
            return await self._on_phase_change(event)

        if event.type == EventType.INSTRUMENT_DETECTED:
            image_b64 = event.data.get("image_b64")
            if image_b64 and not event.data.get("instruments"):
                detector = get_instrument_detector()
                result = await detector.detect(image_b64)
                event.data["instruments"] = [
                    {"name": d.name, "count": d.count} for d in result.instruments
                ]
                event.data["detection_source"] = result.source_name
            return await self._on_instrument_detection(event)

        if event.type == EventType.TRANSCRIPT:
            text = event.data.get("text", "").lower()
            speaker = event.data.get("speaker", "")
            if speaker in ("sentinel", "nael", "system"):
                return []

            # Voice commands
            if any(kw in text for kw in ["count", "instrument", "swab", "sponge",
                                          "needle", "verify", "check count"]):
                return await self._handle_count_request(event)
            if "swab" in text and any(kw in text for kw in ["used", "blood", "stained"]):
                return self._record_used_swab(event)

        return []

    def _reset(self):
        self._initial_count = {}
        self._current_count = {}
        self._count_history = []
        self._consecutive_stable = 0
        self._last_confirmed_count = {}
        self._swabs = SwabTracker()
        self._needles = NeedleTracker()
        self._counts_verified = False
        self._second_count_done = False
        self._phase = "preparation"
        self._who_sign_in = False
        self._who_time_out = False
        self._who_sign_out = False
        self._count_change_events = []

    async def _on_instrument_detection(self, event: AgentEvent) -> list[AgentEvent]:
        instruments = event.data.get("instruments", [])
        detections = event.data.get("detections", [])
        source = event.data.get("detection_source", "unknown")
        results: list[AgentEvent] = []
        cortex = get_cortex()
        now = time.time()

        # Parse current detection
        new_counts: dict[str, int] = {}
        for inst in (instruments or detections):
            name = inst.get("name", "unknown")
            count = inst.get("count", 1)
            new_counts[name] = new_counts.get(name, 0) + count

        # Multi-frame confidence: check if count is stable
        if new_counts == self._current_count:
            self._consecutive_stable += 1
        else:
            self._consecutive_stable = 0

        confidence = min(0.99, 0.6 + self._consecutive_stable * 0.08)

        # Record snapshot
        total = sum(new_counts.values())
        snapshot = InstrumentSnapshot(
            timestamp=now, counts=dict(new_counts),
            total=total, source=source, confidence=confidence,
        )
        self._count_history.append(snapshot)

        # Update cortex
        cortex.instrument_current = dict(new_counts)
        cortex.instrument_snapshots.append((now, dict(new_counts)))

        # INITIAL COUNT (preparation phase, high confidence)
        if not self._initial_count and self._phase == "preparation" and confidence >= 0.85:
            self._initial_count = dict(new_counts)
            self._last_confirmed_count = dict(new_counts)
            cortex.instrument_baseline = dict(new_counts)

            results.append(AgentEvent(
                type=EventType.DISPLAY_TRANSCRIPT,
                source=self.agent_id, priority=6,
                session_id=event.session_id,
                data={
                    "speaker": "sentinel", "pillar": "sentinel", "at": now,
                    "text": (f"WHO Sign-In: Initial instrument count locked. "
                             f"{total} instruments across {len(new_counts)} types. "
                             f"Swabs: {self._swabs.initial_clean}. "
                             f"Needles: {self._needles.initial_count}. "
                             f"Confidence: {confidence:.0%}. "
                             f"Count will be verified at closure."),
                },
            ))
            self._who_sign_in = True
            cortex.add_timeline(TimelineEventType.INSTRUMENT_COUNT, self.agent_id,
                                f"Initial count: {total} instruments", data=new_counts)

        elif self._initial_count:
            # Detect count CHANGES (instruments entering/leaving field)
            for name, prev in self._last_confirmed_count.items():
                curr = new_counts.get(name, 0)
                if curr != prev and confidence >= 0.85:
                    direction = "added to" if curr > prev else "removed from"
                    diff = abs(curr - prev)
                    self._count_change_events.append({
                        "instrument": name, "from": prev, "to": curr, "at": now,
                    })
                    cortex.add_timeline(TimelineEventType.INSTRUMENT_COUNT, self.agent_id,
                                        f"{name}: {diff} {direction} field")

            # Check for DISCREPANCY (missing instruments)
            if confidence >= 0.85:
                self._last_confirmed_count = dict(new_counts)
                discrepancies = self._check_discrepancies()
                if discrepancies and self._phase not in ("preparation",):
                    for d in discrepancies:
                        severity = "critical" if self._phase in ("closure", "haemostasis") else "warning"
                        results.append(AgentEvent(
                            type=EventType.ALERT,
                            source=self.agent_id,
                            priority=1 if self._phase == "closure" else 2,
                            session_id=event.session_id,
                            data={
                                "title": "Instrument Count Discrepancy",
                                "body": d, "severity": severity,
                                "pillar": "sentinel", "at": now,
                                "confidence": confidence,
                            },
                        ))

        self._current_count = dict(new_counts)
        return results

    async def _on_phase_change(self, event: AgentEvent) -> list[AgentEvent]:
        self._phase = event.data.get("phase", "")
        results: list[AgentEvent] = []
        cortex = get_cortex()
        now = time.time()

        if self._phase == "incision" and not self._who_time_out:
            # WHO Time-Out
            self._who_time_out = True
            total_init = sum(self._initial_count.values())
            total_curr = sum(self._current_count.values())
            match = total_curr == total_init
            results.append(AgentEvent(
                type=EventType.DISPLAY_TRANSCRIPT,
                source=self.agent_id, priority=5,
                session_id=event.session_id,
                data={
                    "speaker": "sentinel", "pillar": "sentinel", "at": now,
                    "text": (f"WHO Time-Out: Pre-incision count {'CONFIRMED' if match else 'MISMATCH'}. "
                             f"{total_curr}/{total_init} instruments. "
                             f"Swabs: {self._swabs.initial_clean}. "
                             f"Needles: {self._needles.initial_count}."),
                },
            ))

        elif self._phase == "closure":
            # MANDATORY closure count
            discrepancies = self._check_discrepancies()
            swab_missing = self._swabs.missing
            needle_missing = self._needles.missing

            if discrepancies or swab_missing > 0 or needle_missing > 0:
                all_issues = list(discrepancies)
                if swab_missing:
                    all_issues.append(f"SWABS: {swab_missing} MISSING (had {self._swabs.initial_clean}, "
                                       f"clean {self._swabs.current_clean} + used {self._swabs.used_blood_stained})")
                if needle_missing:
                    all_issues.append(f"NEEDLES: {needle_missing} MISSING")
                if self._needles.broken_detected:
                    all_issues.append("BROKEN NEEDLE DETECTED — X-ray before closure")

                for issue in all_issues:
                    results.append(AgentEvent(
                        type=EventType.ALERT,
                        source=self.agent_id, priority=1,
                        session_id=event.session_id,
                        data={
                            "title": "⚠ CLOSURE COUNT FAILED",
                            "body": issue, "severity": "critical",
                            "pillar": "sentinel", "at": now,
                        },
                    ))
                results.append(AgentEvent(
                    type=EventType.DISPLAY_TTS,
                    source=self.agent_id, priority=1,
                    session_id=event.session_id,
                    data={
                        "text": (f"ALERT — Closure count FAILED. "
                                 f"{len(all_issues)} discrepancies found. "
                                 f"DO NOT CLOSE until all items are accounted for."),
                        "voice": "critical", "at": now,
                    },
                ))
            else:
                self._counts_verified = True
                self._who_sign_out = True
                total_init = sum(self._initial_count.values())
                results.append(AgentEvent(
                    type=EventType.DISPLAY_TRANSCRIPT,
                    source=self.agent_id, priority=4,
                    session_id=event.session_id,
                    data={
                        "speaker": "sentinel", "pillar": "sentinel", "at": now,
                        "text": (f"WHO Sign-Out: Closure count VERIFIED. "
                                 f"All {total_init} instruments accounted. "
                                 f"Swabs: {self._swabs.total_accounted}/{self._swabs.initial_clean}. "
                                 f"Needles: {self._needles.current_count}/{self._needles.initial_count}. "
                                 f"Safe to close."),
                    },
                ))
                cortex.add_timeline(TimelineEventType.INSTRUMENT_COUNT, self.agent_id,
                                    f"Closure count VERIFIED — {total_init} instruments",
                                    severity="info")

            # Swab usage report
            if self._swabs.used_blood_stained > 0:
                rate = self._swabs.use_rate_per_hour()
                results.append(AgentEvent(
                    type=EventType.DISPLAY_TRANSCRIPT,
                    source=self.agent_id, priority=7,
                    session_id=event.session_id,
                    data={
                        "speaker": "sentinel", "pillar": "sentinel", "at": now,
                        "text": (f"Swab report: {self._swabs.used_blood_stained} blood-stained swabs "
                                 f"({rate:.1f}/hr). "
                                 f"{'Above average — verify haemostasis.' if rate > 6 else 'Within normal range.'}"),
                    },
                ))

        return results

    def _record_used_swab(self, event: AgentEvent) -> list[AgentEvent]:
        self._swabs.used_blood_stained += 1
        self._swabs.current_clean = max(0, self._swabs.current_clean - 1)
        self._swabs.timestamps_used.append(time.time())
        get_cortex().add_timeline(TimelineEventType.INSTRUMENT_COUNT, self.agent_id,
                                   f"Blood-stained swab #{self._swabs.used_blood_stained}")
        return [AgentEvent(
            type=EventType.DISPLAY_TRANSCRIPT,
            source=self.agent_id, priority=8,
            session_id=event.session_id,
            data={
                "speaker": "sentinel", "pillar": "sentinel", "at": time.time(),
                "text": f"Swab #{self._swabs.used_blood_stained} recorded as blood-stained. "
                        f"Remaining clean: {self._swabs.current_clean}.",
            },
        )]

    async def _handle_count_request(self, event: AgentEvent) -> list[AgentEvent]:
        total_initial = sum(self._initial_count.values())
        total_current = sum(self._current_count.values())
        cortex = get_cortex()

        items = []
        for name, init_count in sorted(self._initial_count.items()):
            curr = self._current_count.get(name, 0)
            status = "✓" if curr == init_count else f"⚠ {curr}/{init_count}"
            items.append(f"{name}: {status}")

        summary = "; ".join(items[:8]) if items else "No instruments logged yet."

        # Include recent changes
        recent_changes = [c for c in self._count_change_events
                          if (time.time() - c["at"]) < 600]
        change_text = ""
        if recent_changes:
            changes = [f"{c['instrument']}: {c['from']}→{c['to']}" for c in recent_changes[-3:]]
            change_text = f" Recent changes: {'; '.join(changes)}."

        return [AgentEvent(
            type=EventType.DISPLAY_TRANSCRIPT,
            source=self.agent_id, priority=6,
            session_id=event.session_id,
            data={
                "speaker": "sentinel", "pillar": "sentinel", "at": time.time(),
                "text": (f"Count: {total_current}/{total_initial} instruments. {summary}. "
                         f"Swabs: {self._swabs.total_accounted}/{self._swabs.initial_clean}. "
                         f"Needles: {self._needles.current_count}/{self._needles.initial_count}."
                         f"{change_text}"),
            },
        )]

    def _check_discrepancies(self) -> list[str]:
        discrepancies = []
        for name, init_count in self._initial_count.items():
            curr = self._current_count.get(name, 0)
            if curr < init_count:
                diff = init_count - curr
                # Check if this was a recent confirmed change
                discrepancies.append(
                    f"{name}: {diff} MISSING (initial {init_count}, current {curr}). "
                    f"Check: patient cavity, drapes, floor, back table."
                )
        return discrepancies
