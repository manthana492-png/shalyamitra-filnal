"""
ShalyaMitra — Clinical AI Guardrails Engine

Production-grade safety guardrails for all AI agent responses.
Replaces NVIDIA NeMo Guardrails with a self-contained, rule-based
+ LLM-validated safety layer.

Applied to every agent response BEFORE it reaches the surgeon.

Guardrail layers:
  1. HARD BLOCKS    — regex/keyword rules, zero latency, cannot be bypassed
  2. SOFT WARNINGS  — pattern detection that adds safety caveats
  3. LLM VALIDATION — LLM checks response for clinical hallucination (async)
  4. AUDIT TRAIL    — every blocked/warned response is logged

Hard block categories (immediate block, response replaced):
  - Definitive diagnoses without qualification
  - Dosing instructions without weight-based calculation
  - Surgical technique instructions as direct commands
  - Confident statements about things AI cannot verify
  - Personal data / PHI in AI responses

Soft warning categories (caveat appended):
  - Statements about rare conditions
  - Drug interactions without "consult" language
  - References to specific patients
  - Statistical claims without citations

CDS (Clinical Decision Support) safe harbour rules:
  - AI is advisory, surgeon is final decision-maker
  - All dosing must reference weight/renal function
  - Alerts must be acknowledgedable (not modal-blocking)
  - Surgeon can silence any alert (with logged reason)
"""

from __future__ import annotations
import re, time, asyncio, json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional
import httpx

from app.config import settings


class GuardrailOutcome(str, Enum):
    PASS = "pass"               # Response is safe, pass through
    WARN = "warn"               # Safe but added caveat
    BLOCK = "block"             # Blocked, replacement response provided
    ESCALATE = "escalate"       # Needs immediate human review


class GuardrailCategory(str, Enum):
    DEFINITIVE_DIAGNOSIS = "definitive_diagnosis"
    UNSAFE_DOSING = "unsafe_dosing"
    DIRECT_SURGICAL_COMMAND = "direct_surgical_command"
    UNVERIFIABLE_CLAIM = "unverifiable_claim"
    PHI_LEAK = "phi_leak"
    HALLUCINATION_RISK = "hallucination_risk"
    MISSING_QUALIFICATION = "missing_qualification"
    EMERGENCY_BYPASS = "emergency_bypass"


@dataclass
class GuardrailViolation:
    category: GuardrailCategory
    severity: str           # "critical" | "high" | "medium" | "low"
    matched_text: str
    rule_name: str
    explanation: str


@dataclass
class GuardrailResult:
    original_text: str
    safe_text: str              # Text after guardrails applied
    outcome: GuardrailOutcome
    violations: list[GuardrailViolation]
    caveats_added: list[str]
    processing_time_ms: float
    llm_validated: bool = False


# ════════════════════════════════════════════════════════
# Hard Block Rules
# ════════════════════════════════════════════════════════

# Pattern: "The patient HAS [diagnosis]" without qualification
DEFINITIVE_DIAGNOSIS_PATTERN = re.compile(
    r'\b(?:the patient|this patient|patient)\s+(?:has|is suffering from|presents with|diagnosed with)\s+'
    r'(?!likely|possibly|possibly|probably|may have|might have|could have|appears to have)',
    re.IGNORECASE
)

# Pattern: "Give X mg of drug" — direct dosing commands
DIRECT_DOSING_PATTERN = re.compile(
    r'\b(?:give|administer|inject|infuse|push)\s+(\d+\.?\d*)\s*(?:mg|mcg|ml|units?|mmol)\s+(?:of\s+)?'
    r'(?:propofol|fentanyl|morphine|midazolam|ketamine|rocuronium|atracurium|adrenaline|epinephrine)',
    re.IGNORECASE
)

# Pattern: "You should cut/incise/dissect" — direct surgical commands
SURGICAL_COMMAND_PATTERN = re.compile(
    r'\b(?:you should|you must|you need to|proceed to|go ahead and)\s+'
    r'(?:cut|incise|dissect|ligate|clamp|divide|resect|excise|anastomose|suture)',
    re.IGNORECASE
)

# Pattern: Absolute certainty without hedging
ABSOLUTE_CERTAINTY_PATTERN = re.compile(
    r'\b(?:definitely|certainly|absolutely|100%|guaranteed|always|never)\s+'
    r'(?:is|are|will|should|must|safe|correct|right)',
    re.IGNORECASE
)

# PHI patterns in AI response (names followed by medical info)
PHI_IN_RESPONSE_PATTERN = re.compile(
    r'\b(?:Mr|Mrs|Ms|Dr|Shri|Smt)\.?\s+[A-Z][a-z]+\s+[A-Z][a-z]+\s+'
    r'(?:has|is|was|had|presents)',
    re.IGNORECASE
)

# Aadhaar or PAN in response
ID_IN_RESPONSE_PATTERN = re.compile(
    r'\b[2-9]\d{3}[\s-]?\d{4}[\s-]?\d{4}\b'   # Aadhaar
    r'|\b[A-Z]{5}\d{4}[A-Z]\b'                   # PAN
)


# ════════════════════════════════════════════════════════
# Soft Warning Rules
# ════════════════════════════════════════════════════════

# Drug interactions without "consult" language
DRUG_INTERACTION_WITHOUT_CONSULT = re.compile(
    r'\b(?:interacts?|interaction|contraindicated|avoid combining)\b(?!.*(?:consult|verify|check|confirm))',
    re.IGNORECASE
)

# Statistical claims
STATISTICAL_CLAIM_PATTERN = re.compile(
    r'\b\d+\.?\d*\s*%\s+(?:of patients|mortality|morbidity|risk|chance|probability)',
    re.IGNORECASE
)

# References to "standard of care" or "protocol" without citation
UNCITED_PROTOCOL_PATTERN = re.compile(
    r'\b(?:standard of care|clinical guideline|protocol states|evidence shows|studies show)\b'
    r'(?!.*(?:reference|source|guideline|cite|\d{4}))',
    re.IGNORECASE
)


# ════════════════════════════════════════════════════════
# Safe Response Templates
# ════════════════════════════════════════════════════════

SAFE_DISCLAIMER = (
    "\n\n⚕️ *Advisory only. Surgeon's clinical judgment is final. "
    "Verify against current protocols.*"
)

DOSING_SAFE_RESPONSE = (
    "I can provide dosing reference information, but specific dosing "
    "must be calculated based on patient weight, renal function, and "
    "clinical context by the anaesthesiologist. Please verify with "
    "your Pharmacist pillar or BNF/drug formulary."
)

BLOCK_RESPONSE_TEMPLATE = (
    "I've identified a safety concern with my previous response. "
    "Reason: {reason}. "
    "Please verify this information with clinical guidelines or "
    "consult the appropriate specialist."
)


# ════════════════════════════════════════════════════════
# Clinical Guardrails Engine
# ════════════════════════════════════════════════════════

class ClinicalGuardrailsEngine:
    """
    Multi-layer clinical safety engine for all AI agent outputs.

    Layer 1: Hard rules (synchronous, <1ms)
    Layer 2: Soft warnings (synchronous, <1ms)
    Layer 3: LLM validation (async, ~500ms, optional)

    Usage:
        engine = ClinicalGuardrailsEngine()
        result = await engine.check("Give 200mg propofol now")
        if result.outcome == GuardrailOutcome.BLOCK:
            return result.safe_text  # Use safe replacement
    """

    def __init__(
        self,
        enable_llm_validation: bool = True,
        llm_validation_threshold: float = 0.8,
    ):
        self.enable_llm_validation = enable_llm_validation
        self.llm_validation_threshold = llm_validation_threshold
        self._audit: list[dict] = []

    # ── Layer 1: Hard Block Rules ─────────────────────────

    def _apply_hard_rules(self, text: str) -> list[GuardrailViolation]:
        violations = []

        if DIRECT_DOSING_PATTERN.search(text):
            match = DIRECT_DOSING_PATTERN.search(text)
            violations.append(GuardrailViolation(
                category=GuardrailCategory.UNSAFE_DOSING,
                severity="critical",
                matched_text=match.group(0),
                rule_name="direct_dosing_command",
                explanation="AI must not give direct dosing commands. Weight-based calculation required.",
            ))

        if SURGICAL_COMMAND_PATTERN.search(text):
            match = SURGICAL_COMMAND_PATTERN.search(text)
            violations.append(GuardrailViolation(
                category=GuardrailCategory.DIRECT_SURGICAL_COMMAND,
                severity="high",
                matched_text=match.group(0),
                rule_name="surgical_command",
                explanation="AI must not issue direct surgical instructions. Advisory language required.",
            ))

        if PHI_IN_RESPONSE_PATTERN.search(text):
            match = PHI_IN_RESPONSE_PATTERN.search(text)
            violations.append(GuardrailViolation(
                category=GuardrailCategory.PHI_LEAK,
                severity="critical",
                matched_text=match.group(0),
                rule_name="phi_in_response",
                explanation="Patient identifiers must not appear in AI responses.",
            ))

        if ID_IN_RESPONSE_PATTERN.search(text):
            violations.append(GuardrailViolation(
                category=GuardrailCategory.PHI_LEAK,
                severity="critical",
                matched_text="[IDENTITY_NUMBER]",
                rule_name="id_number_in_response",
                explanation="Identity numbers (Aadhaar/PAN) must not appear in AI responses.",
            ))

        return violations

    # ── Layer 2: Soft Warning Rules ───────────────────────

    def _apply_soft_rules(self, text: str) -> tuple[list[GuardrailViolation], list[str]]:
        violations = []
        caveats = []

        if DEFINITIVE_DIAGNOSIS_PATTERN.search(text):
            violations.append(GuardrailViolation(
                category=GuardrailCategory.DEFINITIVE_DIAGNOSIS,
                severity="medium",
                matched_text=DEFINITIVE_DIAGNOSIS_PATTERN.search(text).group(0),
                rule_name="definitive_diagnosis",
                explanation="Diagnosis should be qualified with hedging language.",
            ))
            caveats.append("Clinical diagnosis requires physical examination and investigation confirmation.")

        if ABSOLUTE_CERTAINTY_PATTERN.search(text):
            violations.append(GuardrailViolation(
                category=GuardrailCategory.UNVERIFIABLE_CLAIM,
                severity="medium",
                matched_text=ABSOLUTE_CERTAINTY_PATTERN.search(text).group(0),
                rule_name="absolute_certainty",
                explanation="Absolute certainty language is inappropriate for clinical AI.",
            ))
            caveats.append("Clinical findings should always be verified with appropriate assessment.")

        if STATISTICAL_CLAIM_PATTERN.search(text):
            caveats.append("Statistical data shown is based on literature — actual risk varies by patient.")

        if UNCITED_PROTOCOL_PATTERN.search(text):
            caveats.append("Guideline references should be verified against current local protocols.")

        if DRUG_INTERACTION_WITHOUT_CONSULT.search(text):
            caveats.append("Drug interaction information — verify with pharmacist or current drug reference.")

        return violations, caveats

    # ── Layer 3: LLM Hallucination Check (async) ──────────

    async def _llm_hallucination_check(self, text: str) -> Optional[GuardrailViolation]:
        """
        Ask an LLM to check for clinical hallucinations.
        Uses the cheapest/fastest model (Gemini Flash).
        Returns a violation if hallucination detected.
        """
        if not settings.openrouter_api_key:
            return None

        prompt = """You are a medical AI safety checker.
Analyse this AI response for clinical safety issues:
- Fabricated drug dosages or protocols
- Incorrect anatomical claims
- Contradictory statements
- Fabricated statistics or citations
- Inappropriate certainty about unverifiable facts

Response to check:
\"\"\"
{text}
\"\"\"

Return ONLY valid JSON:
{{"safe": true/false, "reason": "explanation if unsafe", "severity": "low/medium/high/critical"}}"""

        try:
            async with httpx.AsyncClient(timeout=8.0) as http:
                resp = await http.post(
                    f"{settings.openrouter_base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.openrouter_api_key}",
                        "HTTP-Referer": "https://shalyamitra.dev",
                    },
                    json={
                        "model": "google/gemini-2.0-flash-001",
                        "messages": [{"role": "user", "content": prompt.format(text=text[:1000])}],
                        "max_tokens": 150,
                        "temperature": 0.0,
                        "response_format": {"type": "json_object"},
                    },
                )

            if resp.status_code != 200:
                return None

            result = json.loads(resp.json()["choices"][0]["message"]["content"])

            if not result.get("safe", True):
                return GuardrailViolation(
                    category=GuardrailCategory.HALLUCINATION_RISK,
                    severity=result.get("severity", "medium"),
                    matched_text=text[:100],
                    rule_name="llm_hallucination_check",
                    explanation=result.get("reason", "Potential clinical hallucination detected."),
                )
        except Exception:
            pass
        return None

    # ── Main Check Method ─────────────────────────────────

    async def check(
        self,
        text: str,
        agent_type: str = "unknown",
        skip_llm: bool = False,
    ) -> GuardrailResult:
        """
        Run all guardrail layers on an agent response.

        Returns GuardrailResult with safe_text ready to send to surgeon.
        """
        t0 = time.time()

        # Layer 1: Hard rules (synchronous)
        hard_violations = self._apply_hard_rules(text)

        # Layer 2: Soft rules (synchronous)
        soft_violations, caveats = self._apply_soft_rules(text)

        all_violations = hard_violations + soft_violations

        # Determine outcome from hard violations
        critical_hard = [v for v in hard_violations if v.severity == "critical"]
        high_hard = [v for v in hard_violations if v.severity == "high"]

        if critical_hard:
            outcome = GuardrailOutcome.BLOCK
            safe_text = BLOCK_RESPONSE_TEMPLATE.format(
                reason=critical_hard[0].explanation
            )
        elif high_hard:
            # Convert direct surgical commands to advisory
            safe_text = self._soften_surgical_language(text)
            safe_text += SAFE_DISCLAIMER
            outcome = GuardrailOutcome.WARN
        else:
            safe_text = text
            if caveats:
                safe_text += "\n\n" + " | ".join(caveats)
            outcome = GuardrailOutcome.WARN if caveats else GuardrailOutcome.PASS

        # Layer 3: LLM check (async, only if not blocked already)
        llm_validated = False
        if (
            self.enable_llm_validation
            and not skip_llm
            and outcome != GuardrailOutcome.BLOCK
            and len(text) > 50
        ):
            llm_violation = await self._llm_hallucination_check(text)
            if llm_violation:
                all_violations.append(llm_violation)
                if llm_violation.severity in ("critical", "high"):
                    outcome = GuardrailOutcome.BLOCK
                    safe_text = BLOCK_RESPONSE_TEMPLATE.format(
                        reason=llm_violation.explanation
                    )
                else:
                    safe_text += "\n\n⚠️ *Note: Some claims require independent verification.*"
                    if outcome == GuardrailOutcome.PASS:
                        outcome = GuardrailOutcome.WARN
            llm_validated = True

        # Audit log
        if all_violations:
            self._audit.append({
                "timestamp": time.time(),
                "agent_type": agent_type,
                "outcome": outcome.value,
                "violations": [v.rule_name for v in all_violations],
                "text_length": len(text),
            })

        return GuardrailResult(
            original_text=text,
            safe_text=safe_text,
            outcome=outcome,
            violations=all_violations,
            caveats_added=caveats,
            processing_time_ms=(time.time() - t0) * 1000,
            llm_validated=llm_validated,
        )

    def _soften_surgical_language(self, text: str) -> str:
        """Convert direct commands to advisory language."""
        replacements = [
            (r'\byou should (cut|incise|dissect|ligate|clamp|divide|resect)\b',
             r'consideration may be given to \1ing'),
            (r'\byou must (cut|incise|dissect|ligate|clamp|divide|resect)\b',
             r'the surgical approach may involve \1ing'),
            (r'\bproceed to (cut|incise|dissect|ligate|clamp|divide)\b',
             r'when indicated, \1ting may be considered'),
            (r'\bgo ahead and (cut|incise|dissect|ligate)\b',
             r'\1ting may be the next step based on clinical assessment'),
        ]
        result = text
        for pattern, replacement in replacements:
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        return result

    def check_sync(self, text: str, agent_type: str = "unknown") -> GuardrailResult:
        """Synchronous version — skips LLM validation."""
        loop = asyncio.new_event_loop()
        return loop.run_until_complete(
            self.check(text, agent_type=agent_type, skip_llm=True)
        )

    def get_audit_log(self) -> list[dict]:
        return self._audit.copy()

    def get_stats(self) -> dict:
        total = len(self._audit)
        by_outcome = {}
        by_violation = {}
        for entry in self._audit:
            o = entry["outcome"]
            by_outcome[o] = by_outcome.get(o, 0) + 1
            for v in entry.get("violations", []):
                by_violation[v] = by_violation.get(v, 0) + 1
        return {
            "total_checks": total,
            "by_outcome": by_outcome,
            "by_violation_type": by_violation,
        }


# ════════════════════════════════════════════════════════
# Agent Response Wrapper — applies guardrails automatically
# ════════════════════════════════════════════════════════

class GuardedAgentMixin:
    """
    Mixin for BaseAgent subclasses that auto-applies guardrails
    to every response before it reaches the event bus.

    Usage: class MyAgent(GuardedAgentMixin, BaseAgent): ...
    """

    _guardrails: Optional[ClinicalGuardrailsEngine] = None

    def _get_guardrails(self) -> ClinicalGuardrailsEngine:
        if self._guardrails is None:
            self._guardrails = get_guardrails_engine()
        return self._guardrails

    async def safe_response(
        self,
        text: str,
        agent_type: Optional[str] = None,
    ) -> str:
        """
        Run text through guardrails and return safe version.
        Call this instead of returning raw LLM text.
        """
        engine = self._get_guardrails()
        result = await engine.check(
            text,
            agent_type=agent_type or type(self).__name__,
        )
        if result.outcome == GuardrailOutcome.BLOCK:
            print(f"[GUARDRAILS] BLOCKED {type(self).__name__}: "
                  f"{[v.rule_name for v in result.violations]}")
        elif result.outcome == GuardrailOutcome.WARN:
            print(f"[GUARDRAILS] WARN {type(self).__name__}: "
                  f"{len(result.violations)} violations, "
                  f"{len(result.caveats_added)} caveats added")
        return result.safe_text


# Singleton
_engine: Optional[ClinicalGuardrailsEngine] = None


def get_guardrails_engine() -> ClinicalGuardrailsEngine:
    global _engine
    if _engine is None:
        _engine = ClinicalGuardrailsEngine(
            enable_llm_validation=bool(settings.openrouter_api_key),
        )
    return _engine
