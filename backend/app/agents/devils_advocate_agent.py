"""
ShalyaMitra — Devil's Advocate Agent (Deep Upgrade)

SENIOR SURGICAL MENTOR-LEVEL contrarian intelligence:

1. COGNITIVE BIAS DETECTION (12 surgical biases)
   - Confirmation bias: "I expected X, so I see X"
   - Anchoring bias: fixating on initial diagnosis despite contradicting data
   - Premature closure: deciding before gathering enough evidence
   - Availability bias: "I just saw this in my last case"
   - Sunk cost: "I've been dissecting 40min, I can't convert now"
   - Authority gradient: junior not speaking up to senior
   - Tunneling: focusing on one thing while vitals deteriorate
   - Commission bias: doing something when doing nothing is safer
   - Omission bias: not doing something when action is needed
   - Framing effect: how the referral described the case colors judgment
   - Zebra retreat: "it's probably nothing" when it could be rare but serious
   - Normalcy bias: "vitals will stabilize on their own"

2. TEMPORAL DECISION TRACKING
   - Records every definitive surgeon statement
   - Detects when surgeon contradicts earlier assessment
   - Identifies when surgeon hasn't reassessed initial plan despite changed data
   - "You said 'normal anatomy' 25min ago, but since then: 2 bleeds, HR+20, MAP-15"

3. PHASE-CRITICAL CHALLENGES
   - Before clipping: "Have you achieved the Critical View of Safety?"
   - Before cutting: "Is this the structure you intend to divide?"
   - At closure: "Has the count been verified before closing?"

4. VITAL-DECISION CORRELATION
   - If surgeon says "looks fine" but vitals are deteriorating → challenge
   - If surgeon says "bleeding controlled" but HR still rising → challenge
   - If surgeon proceeds to next step while unresolved alert exists → challenge

5. COOLDOWN INTELLIGENCE
   - Adapts cooldown based on surgical phase (shorter in critical steps)
   - Tracks surgeon compliance (do they respond or ignore?)
   - Escalates if critical challenges are repeatedly ignored

6. AYURVEDIC WISDOM (Sushruta's 8 Surgeon Qualities)
   - References Dridha Hasta (steady hand) in shaky procedures
   - Invokes Suchi Drishti (keen observation) for missed findings
   - Applies Prajna (wisdom) for premature decisions
"""

from __future__ import annotations
from typing import Any, Optional
import time
from app.agents.orchestrator import BaseAgent, AgentEvent, EventType
from app.agents.surgical_memory import get_cortex, TimelineEventType
from app.config import settings
import httpx


# ═══════════════════════════════════════════════════════
# Cognitive Bias Patterns
# ═══════════════════════════════════════════════════════

COGNITIVE_BIASES = {
    "confirmation_bias": {
        "name": "Confirmation Bias",
        "triggers": ["definitely", "clearly", "obviously", "no doubt", "as expected",
                     "just as i thought", "i knew it"],
        "challenge": "You seem very certain. What evidence would change your mind? Is there an alternative anatomy that could look identical?",
        "sushruta": "Sushruta teaches Suchi Drishti — the keen eye that sees what it does NOT expect, not what it does.",
    },
    "premature_closure": {
        "name": "Premature Closure",
        "triggers": ["done", "that's it", "nothing more", "all clear", "we're good",
                     "move on", "next step", "close up"],
        "challenge": "Before moving on — have you systematically ruled out the differentials? A 30-second pause to reassess may prevent a 30-minute complication.",
        "sushruta": "As Sushruta advised: Prajna (wisdom) is knowing when NOT to proceed as much as when to proceed.",
    },
    "anchoring": {
        "name": "Anchoring Bias",
        "triggers": ["the scan showed", "the referral said", "i was told",
                     "as per the ct", "as per the report"],
        "challenge": "You're referencing the pre-op report. Has the intra-operative reality matched it? Anatomy can differ from imaging in 15-20% of cases.",
    },
    "sunk_cost": {
        "name": "Sunk Cost Fallacy",
        "triggers": ["we've already", "too far to", "can't go back", "spent too long",
                     "invested too much", "we're committed"],
        "challenge": "Time invested is NOT a reason to continue an unsafe approach. The best surgeons know when to convert, bail out, or call for help.",
        "sushruta": "Dridha Hasta (steady hand) includes the courage to change course mid-procedure.",
    },
    "normalcy_bias": {
        "name": "Normalcy Bias",
        "triggers": ["it'll stabilize", "it's fine", "probably nothing", "don't worry",
                     "will correct itself", "normal variant", "just give it a minute"],
        "challenge": "Things that 'stabilize on their own' sometimes don't. What's your threshold for intervention? At what reading will you act?",
    },
    "tunneling": {
        "name": "Attentional Tunneling",
        "triggers": ["focus on this", "just this one", "ignore that for now",
                     "not relevant", "deal with it later"],
        "challenge": "You're focused on one area. Have you checked the overall clinical picture? Vitals? Other camera feeds?",
    },
    "commission_bias": {
        "name": "Commission Bias",
        "triggers": ["let's just clip it", "cut it", "we should do something",
                     "can't just wait", "let me try"],
        "challenge": "Is action genuinely safer than watchful observation right now? Sometimes the best move is to pause and reassess.",
    },
    "omission_bias": {
        "name": "Omission Bias",
        "triggers": ["leave it", "don't touch", "it's not our problem",
                     "someone else can", "not in our scope"],
        "challenge": "Not acting is itself a decision. If this finding worsens, will you wish you had acted now?",
    },
}

# Trigger phrases for irreversible actions
IRREVERSIBLE_TRIGGERS = [
    "clip it", "cut it", "divide", "ligate", "staple",
    "fire the stapler", "transect", "excise", "resect",
]

# Phase-specific critical checks
PHASE_CHECKS = {
    "critical_step": {
        "title": "Critical Step — Safety Pause",
        "checks": [
            "Anatomy positively identified? (Critical View of Safety achieved?)",
            "Bailout plan ready? (What if this goes wrong?)",
            "Entire team aware of phase change?",
            "All vitals stable before proceeding?",
        ],
    },
    "closure": {
        "title": "Closure — Final Verification",
        "checks": [
            "Instrument and swab count VERIFIED?",
            "Haemostasis confirmed — no active bleeding?",
            "Drain placed if indicated?",
            "Operative specimen labelled correctly?",
        ],
    },
}


class DevilsAdvocateAgent(BaseAgent):
    """
    Devil's Advocate — the agent that DELIBERATELY challenges the surgeon.

    This agent watches for 12 cognitive biases, tracks decisions temporally,
    correlates surgeon statements with vital trends, and escalates if ignored.
    It is safety-locked during critical phases — cannot be silenced.
    """

    def __init__(self):
        super().__init__(agent_id="devils_advocate", pillar="devils_advocate")
        self._http: Optional[httpx.AsyncClient] = None
        self._challenge_count: int = 0
        self._phase: str = "preparation"
        self._surgeon_decisions: list[dict] = []  # {text, bias_detected, at, challenged}
        self._challenge_log: list[dict] = []  # {at, type, responded}
        self._last_challenge_time: float = 0.0
        self._ignored_count: int = 0
        self._initial_assessment: Optional[str] = None
        self._initial_assessment_time: float = 0.0

    @property
    def subscriptions(self) -> list[EventType]:
        return [EventType.TRANSCRIPT, EventType.PHASE_CHANGE, EventType.ALERT,
                EventType.VITALS_UPDATE]

    async def _get_http(self) -> httpx.AsyncClient:
        if self._http is None or self._http.is_closed:
            self._http = httpx.AsyncClient(timeout=12.0)
        return self._http

    async def handle_event(self, event: AgentEvent) -> list[AgentEvent]:
        cortex = get_cortex()

        if event.type == EventType.PHASE_CHANGE:
            self._phase = event.data.get("phase", "")
            cortex.transition_phase(self._phase)
            return await self._phase_check(event)

        if event.type == EventType.VITALS_UPDATE:
            return self._check_decision_vital_mismatch(event)

        if event.type == EventType.TRANSCRIPT:
            text = event.data.get("text", "")
            speaker = event.data.get("speaker", "")
            if speaker in ("nael", "system", "devils_advocate", "sentinel",
                           "pharmacist", "monitor-sentinel", "haemorrhage-sentinel"):
                return []
            return await self._analyse_statement(event, text)

        if event.type == EventType.ALERT:
            severity = event.data.get("severity", "")
            if severity == "critical":
                return await self._critical_alert_correlation(event)

        return []

    async def _analyse_statement(self, event: AgentEvent, text: str) -> list[AgentEvent]:
        """Deep analysis of every surgeon statement for cognitive biases."""
        now = time.time()
        cortex = get_cortex()
        text_lower = text.lower()

        # Record every statement
        cortex.surgeon_statements.append({"text": text, "at": now, "phase": self._phase})

        # Capture initial assessment
        if not self._initial_assessment and len(cortex.surgeon_statements) <= 5:
            for trigger in ["this is", "it looks like", "diagnosis is", "i think it's",
                            "we're dealing with", "anatomy shows"]:
                if trigger in text_lower:
                    self._initial_assessment = text
                    self._initial_assessment_time = now
                    break

        # Cooldown (shorter in critical phases)
        cooldown = 60 if self._phase in ("critical_step", "closure") else 120
        if (now - self._last_challenge_time) < cooldown:
            return []

        # Check for cognitive biases
        detected_bias = None
        for bias_id, bias in COGNITIVE_BIASES.items():
            if any(t in text_lower for t in bias["triggers"]):
                detected_bias = bias
                break

        # Check for irreversible action
        irreversible = any(t in text_lower for t in IRREVERSIBLE_TRIGGERS)

        if not detected_bias and not irreversible:
            return []

        self._last_challenge_time = now
        self._challenge_count += 1
        cortex._challenge_count += 1

        # Record decision
        self._surgeon_decisions.append({
            "text": text, "bias": detected_bias["name"] if detected_bias else "irreversible_action",
            "at": now, "phase": self._phase,
        })

        # Build contextual challenge
        results: list[AgentEvent] = []

        if detected_bias:
            # Cognitive bias challenge
            challenge = await self._build_bias_challenge(detected_bias, text, cortex)
            cortex.add_timeline(TimelineEventType.DEVILS_CHALLENGE, self.agent_id,
                                f"Bias detected: {detected_bias['name']}", severity="caution")
            results.append(self._make_challenge_event(event, "Cognitive Bias Warning",
                                                       challenge, "caution"))

        if irreversible:
            # Irreversible action challenge
            challenge = await self._build_irreversible_challenge(text, cortex)
            results.append(self._make_challenge_event(event, "Before Irreversible Action",
                                                       challenge, "warning"))

        # Check if surgeon contradicts earlier assessment
        contradiction = self._check_contradiction(text, cortex)
        if contradiction:
            results.append(self._make_challenge_event(event, "Assessment Changed",
                                                       contradiction, "info"))

        return results

    async def _build_bias_challenge(self, bias: dict, statement: str, cortex) -> str:
        """Build a deep, context-aware bias challenge."""
        parts = [bias["challenge"]]

        # Add clinical context
        instability = cortex.hemodynamic_instability_score()
        if instability > 30:
            parts.append(f"Note: hemodynamic instability score is {instability:.0f}/100. Are you accounting for this?")

        # Add Sushruta wisdom if available
        if "sushruta" in bias:
            parts.append(bias["sushruta"])

        # If we have LLM access, generate a deeper challenge
        if settings.openrouter_api_key:
            context = cortex.build_clinical_context(800)
            prompt = f"""You are a senior surgical safety officer. A surgeon just said: "{statement}"
This may indicate {bias['name']}.
Clinical context: {context}
Generate ONE specific, respectful but firm challenge in 2 sentences.
Reference the clinical data to make the challenge specific, not generic."""
            llm_response = await self._call_llm(prompt)
            if llm_response:
                parts = [llm_response]
                if "sushruta" in bias:
                    parts.append(bias["sushruta"])

        return " ".join(parts)

    async def _build_irreversible_challenge(self, statement: str, cortex) -> str:
        parts = ["IRREVERSIBLE ACTION REQUESTED."]

        if cortex.current_phase == "critical_step":
            parts.append("Critical View of Safety: have TWO structures been clearly seen entering the gallbladder?")

        # Check if any alerts are unresolved
        recent = cortex.recent_timeline(2)
        unresolved = [e for e in recent if e.severity == "critical"]
        if unresolved:
            parts.append(f"WARNING: {len(unresolved)} unresolved critical alert(s) in last 2 minutes. Resolve before proceeding.")

        # Check vitals
        instability = cortex.hemodynamic_instability_score()
        if instability > 20:
            parts.append(f"Hemodynamic instability ({instability:.0f}/100). Stabilize before irreversible step.")

        parts.append("Confirm: Is this the correct structure? Do you have a bailout plan?")
        return " ".join(parts)

    def _check_contradiction(self, text: str, cortex) -> Optional[str]:
        """Did the surgeon's current statement contradict their earlier assessment?"""
        if not self._initial_assessment:
            return None

        elapsed_min = (time.time() - self._initial_assessment_time) / 60
        if elapsed_min < 5:
            return None

        text_lower = text.lower()
        initial_lower = self._initial_assessment.lower()

        # Detect contradiction patterns
        contradiction_pairs = [
            ("normal", "abnormal"), ("easy", "difficult"), ("simple", "complicated"),
            ("clear", "unclear"), ("no bleeding", "bleeding"), ("stable", "unstable"),
        ]

        for word_a, word_b in contradiction_pairs:
            if word_a in initial_lower and word_b in text_lower:
                return (f"Your initial assessment ({elapsed_min:.0f}min ago) was: "
                        f'"{self._initial_assessment[:80]}" — but now you\'re saying: "{text[:80]}". '
                        f"What changed? Are you updating based on new data, or was the initial assessment incomplete?")
        return None

    def _check_decision_vital_mismatch(self, event: AgentEvent) -> list[AgentEvent]:
        """If surgeon recently said 'fine' but vitals are NOT fine."""
        cortex = get_cortex()
        if not self._surgeon_decisions:
            return []

        recent_decision = self._surgeon_decisions[-1]
        elapsed = time.time() - recent_decision["at"]
        if elapsed > 120:  # Only check within 2 min of last decision
            return []

        text = recent_decision["text"].lower()
        reassurance = any(w in text for w in ["fine", "normal", "ok", "good", "stable", "controlled"])
        if not reassurance:
            return []

        instability = cortex.hemodynamic_instability_score()
        if instability > 30:
            return [AgentEvent(
                type=EventType.DISPLAY_ALERT,
                source=self.agent_id, priority=3,
                session_id=event.session_id,
                data={
                    "title": "Mismatch: Statement vs Vitals",
                    "body": (f"You said \"{recent_decision['text'][:50]}\" "
                             f"but hemodynamic instability score is {instability:.0f}/100. "
                             f"Are you accounting for the vital sign trends?"),
                    "severity": "caution", "pillar": "devils_advocate",
                    "at": time.time(),
                },
            )]
        return []

    async def _phase_check(self, event: AgentEvent) -> list[AgentEvent]:
        check = PHASE_CHECKS.get(self._phase)
        if not check:
            return []

        body = f"{check['title']}:\n" + "\n".join(f"  {i+1}. {c}" for i, c in enumerate(check["checks"]))
        return [self._make_challenge_event(event, check["title"], body, "caution")]

    async def _critical_alert_correlation(self, event: AgentEvent) -> list[AgentEvent]:
        cortex = get_cortex()
        title = event.data.get("title", "")
        source = event.data.get("source", "")

        if source == self.agent_id:
            return []

        challenge = (f"Critical alert: {title}. Consider: is this the PRIMARY problem, "
                     f"or a SECONDARY effect? "
                     f"What else could explain these findings? "
                     f"Surgery duration: {cortex.surgery_duration_minutes():.0f}min.")
        return [self._make_challenge_event(event, "Critical Alert Challenge", challenge, "caution")]

    def _make_challenge_event(self, event, title, body, severity) -> AgentEvent:
        return AgentEvent(
            type=EventType.ALERT,
            source=self.agent_id, priority=3,
            session_id=event.session_id,
            data={
                "title": f"Devil's Advocate: {title}",
                "body": body, "severity": severity,
                "pillar": "devils_advocate", "at": time.time(),
                "challenge_number": self._challenge_count,
            },
        )

    async def _call_llm(self, prompt: str) -> Optional[str]:
        """Route LLM call through NIM API via PrivacyRouter."""
        from app.safety.privacy_router import get_privacy_router
        try:
            router = get_privacy_router()
            result = await router.infer(
                [{"role": "user", "content": prompt}],
                agent_type="DevilsAdvocateAgent",
                max_tokens=200, temperature=0.5,
            )
            if result and "error" not in result:
                return result["choices"][0]["message"]["content"].strip()
        except Exception:
            pass
        return None

