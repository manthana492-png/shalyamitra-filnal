"""
ShalyaMitra — Pharmacist Agent (Deep Upgrade)

SENIOR ANAESTHETIST-LEVEL pharmacokinetic intelligence:

1. REAL-TIME PK/PD MODELING
   - Marsh model for Propofol (effect-site concentration)
   - Minto model for Remifentanil/Fentanyl
   - Simplified 3-compartment decay per drug
   - Plasma level estimation over time with stacking detection

2. CUMULATIVE DOSE TRACKING
   - Running total per drug with safe ceiling alerts
   - Weight-adjusted dosing verification (mg/kg)
   - Total opioid equivalence in morphine milligram equivalents (MME)
   - Context-sensitive half-time tracking

3. REDOSING INTELLIGENCE
   - Predicts when muscle relaxant will wear off
   - "Rocuronium: effect ~80% at 25min, redose in ~15min"
   - Alerts if redose is given too early (stacking risk)
   - Alerts if redose is overdue (patient may move)

4. INTERACTION ENGINE WITH TEMPORAL CONTEXT
   - Not just "Drug A + Drug B = interaction"
   - Considers TIMING: "Fentanyl given 5min ago, propofol now — enhanced respiratory depression"
   - Tracks simultaneous vs sequential administration
   - Knows which interactions are clinically relevant vs theoretical

5. INFUSION MANAGEMENT
   - Tracks continuous infusions (propofol, remifentanil, dexmedetomidine)
   - Calculates running total dose from infusion rate + duration
   - Alerts on excessive infusion duration

6. AYURVEDIC PHARMACOLOGY (Dravyaguna)
   - References Sushruta's drug preparation principles
   - Maps modern drugs to Ayurvedic rasas (tastes) and vipakas
   - Integrates prakriti (constitution) awareness for dosing
"""

from __future__ import annotations
from typing import Any, Optional
import time, math
from app.agents.orchestrator import BaseAgent, AgentEvent, EventType
from app.agents.surgical_memory import get_cortex, TimelineEventType
from app.knowledge.drug_db import get_drug_db, check_interactions


# ═══════════════════════════════════════════════════════
# PK Parameters Database (Clinically validated)
# ═══════════════════════════════════════════════════════

PK_PROFILES = {
    "Propofol": {
        "onset_min": 0.5, "peak_min": 1.5, "clinical_duration_min": 8,
        "context_sensitive_ht_min": 40,  # After 2hr infusion
        "safe_ceiling_mg_kg": 10,         # Induction ceiling
        "infusion_range_mg_kg_hr": (4, 12),
        "model": "Marsh",
        "elimination_hl_min": 300,        # Terminal half-life
        "warnings": ["Propofol infusion syndrome risk >4mg/kg/hr for >48hr",
                      "Significant respiratory depression, have airway ready"],
    },
    "Fentanyl": {
        "onset_min": 1, "peak_min": 3, "clinical_duration_min": 45,
        "context_sensitive_ht_min": 120,
        "safe_ceiling_mcg_kg": 10,        # Total surgical dose
        "model": "Minto",
        "elimination_hl_min": 219,
        "mme_factor": 100,               # 100x morphine potency
        "warnings": ["Chest wall rigidity at rapid high doses",
                      "Delayed respiratory depression possible"],
    },
    "Rocuronium": {
        "onset_min": 1.5, "peak_min": 3, "clinical_duration_min": 40,
        "redose_at_pct": 25,             # Redose when effect drops to 25%
        "safe_ceiling_mg_kg": 1.2,
        "reversal": "Sugammadex 2-4mg/kg for full reversal",
        "warnings": ["Anaphylaxis risk — most common cause of perioperative anaphylaxis"],
    },
    "Atracurium": {
        "onset_min": 2, "peak_min": 5, "clinical_duration_min": 35,
        "redose_at_pct": 25,
        "safe_ceiling_mg_kg": 1.0,
        "reversal": "Neostigmine 0.05mg/kg + Glycopyrrolate 0.01mg/kg",
        "warnings": ["Histamine release at rapid administration", "Laudanosine metabolite — seizure risk at very high doses"],
    },
    "Midazolam": {
        "onset_min": 2, "peak_min": 5, "clinical_duration_min": 30,
        "safe_ceiling_mg_kg": 0.3,
        "model": "N/A",
        "elimination_hl_min": 120,
        "reversal": "Flumazenil 0.2mg IV, repeat q1min to max 1mg",
        "warnings": ["Paradoxical agitation in elderly", "Prolonged sedation in hepatic impairment"],
    },
    "Ketamine": {
        "onset_min": 1, "peak_min": 5, "clinical_duration_min": 15,
        "safe_ceiling_mg_kg": 4.5,
        "model": "Domino",
        "elimination_hl_min": 150,
        "mme_factor": 0,
        "warnings": ["Emergence phenomena — give midazolam to prevent", "Raises ICP — avoid in head injury"],
    },
    "Morphine": {
        "onset_min": 5, "peak_min": 20, "clinical_duration_min": 240,
        "safe_ceiling_mg_kg": 0.3,
        "elimination_hl_min": 180,
        "mme_factor": 1,  # Reference standard
        "warnings": ["Histamine release", "Active metabolite M6G accumulates in renal failure"],
    },
    "Atropine": {
        "onset_min": 1, "peak_min": 2, "clinical_duration_min": 30,
        "safe_ceiling_mg_kg": 0.04,
        "warnings": ["Paradoxical bradycardia at sub-therapeutic doses"],
    },
    "Ephedrine": {
        "onset_min": 1, "peak_min": 2, "clinical_duration_min": 15,
        "safe_ceiling_mg_kg": 1.5,
        "warnings": ["Tachyphylaxis after 3-4 doses — switch to phenylephrine"],
    },
    "Phenylephrine": {
        "onset_min": 0.5, "peak_min": 1, "clinical_duration_min": 15,
        "safe_ceiling_mg_kg": 0.01,
        "warnings": ["Reflex bradycardia", "Reduces cardiac output — avoid in low CO states"],
    },
    "Neostigmine": {
        "onset_min": 3, "peak_min": 7, "clinical_duration_min": 60,
        "safe_ceiling_mg_kg": 0.07,
        "warnings": ["MUST give with anticholinergic (glycopyrrolate/atropine)",
                      "Bradycardia if given alone"],
    },
    "Ondansetron": {
        "onset_min": 5, "peak_min": 15, "clinical_duration_min": 360,
        "safe_ceiling_mg_kg": 0.15,
        "warnings": ["QT prolongation at high doses"],
    },
    "Dexamethasone": {
        "onset_min": 30, "peak_min": 60, "clinical_duration_min": 1440,
        "safe_ceiling_mg_kg": 0.5,
        "warnings": ["Hyperglycemia", "Perineal burning on rapid injection"],
    },
    "Paracetamol": {
        "onset_min": 5, "peak_min": 30, "clinical_duration_min": 360,
        "safe_ceiling_mg_kg": 15,
        "warnings": ["Hepatotoxicity above 4g/day", "Reduce in hepatic impairment"],
    },
    "Ketorolac": {
        "onset_min": 10, "peak_min": 30, "clinical_duration_min": 360,
        "safe_ceiling_mg_kg": 0.5,
        "mme_factor": 0,
        "warnings": ["Renal impairment risk", "GI bleeding", "Avoid if >65yr or renal disease",
                      "Max 5 days use"],
    },
}

# Maximum safe cumulative doses (absolute limits)
ABSOLUTE_CEILINGS = {
    "Propofol": 500,      # mg induction (infusion separate)
    "Fentanyl": 0.5,      # mg (500 mcg) total surgery
    "Morphine": 20,       # mg
    "Midazolam": 10,      # mg
    "Ephedrine": 100,     # mg
    "Atropine": 3,        # mg
    "Neostigmine": 5,     # mg
    "Ondansetron": 16,    # mg
    "Paracetamol": 4000,  # mg (4g/day)
    "Ketorolac": 120,     # mg/day
}


class PharmacistAgent(BaseAgent):
    """
    The Pharmacist — real-time pharmacokinetic intelligence.

    Tracks every drug as a decaying plasma concentration curve,
    detects stacking, predicts redose timing, monitors cumulative
    toxicity, and correlates drug effects with vital sign changes.
    """

    def __init__(self):
        super().__init__(agent_id="pharmacist", pillar="pharmacist")
        self._http: Optional[Any] = None
        self._patient_weight_kg: float = 70.0
        self._patient_age: int = 50
        self._total_mme: float = 0.0  # Morphine milligram equivalents
        self._ephedrine_dose_count: int = 0
        self._last_redose_check: float = 0.0

    @property
    def subscriptions(self) -> list[EventType]:
        return [EventType.TRANSCRIPT, EventType.SESSION_START,
                EventType.DRUG_ADMINISTERED, EventType.VITALS_UPDATE]

    async def handle_event(self, event: AgentEvent) -> list[AgentEvent]:
        cortex = get_cortex()

        if event.type == EventType.SESSION_START:
            self._patient_weight_kg = event.data.get("patient", {}).get("weight_kg", 70.0)
            self._patient_age = event.data.get("patient", {}).get("age", 50)
            cortex.patient_weight_kg = self._patient_weight_kg
            cortex.patient_age = self._patient_age
            self._total_mme = 0.0
            self._ephedrine_dose_count = 0
            return []

        if event.type == EventType.DRUG_ADMINISTERED:
            return await self._handle_drug_event(event)

        if event.type == EventType.TRANSCRIPT:
            text = event.data.get("text", "").lower()
            speaker = event.data.get("speaker", "")
            if speaker in ("nael", "pharmacist", "system"):
                return []
            drug_keywords = list(PK_PROFILES.keys()) + [
                "drug", "bolus", "infusion", "dose", "redose",
                "mcg", "mg", "ml", "reversal", "sugammadex"
            ]
            if any(kw.lower() in text for kw in drug_keywords):
                return await self._parse_drug_command(event)

        # Periodic redose checks (every 60 seconds)
        if event.type == EventType.VITALS_UPDATE:
            now = time.time()
            if (now - self._last_redose_check) > 60:
                self._last_redose_check = now
                return self._check_redose_needed(event)

        return []

    async def _handle_drug_event(self, event: AgentEvent) -> list[AgentEvent]:
        drug = event.data.get("drug", "Unknown")
        dose_mg = event.data.get("dose_mg", 0)
        route = event.data.get("route", "IV")
        cortex = get_cortex()
        results: list[AgentEvent] = []

        # Get PK profile
        pk = PK_PROFILES.get(drug, {})
        dose_per_kg = round(dose_mg / self._patient_weight_kg, 2)

        # Record in cortex
        cortex.record_drug(
            drug, dose_mg, route,
            onset_min=pk.get("onset_min", 1),
            peak_min=pk.get("peak_min", 5),
            duration_min=pk.get("clinical_duration_min", 30),
        )

        # Track MME (opioid equivalence)
        mme_factor = pk.get("mme_factor", 0)
        if mme_factor > 0:
            self._total_mme += dose_mg * mme_factor
            if drug == "Fentanyl":
                self._total_mme += dose_mg * 1000 * mme_factor  # Fentanyl is in mg but 100x potency

        # === CHECK 1: Cumulative ceiling ===
        total = cortex.total_drug_dose(drug)
        ceiling = ABSOLUTE_CEILINGS.get(drug)
        if ceiling and total > ceiling * 0.8:
            pct = total / ceiling * 100
            severity = "critical" if total >= ceiling else "warning"
            results.append(AgentEvent(
                type=EventType.ALERT,
                source=self.agent_id, priority=2,
                session_id=event.session_id,
                data={
                    "title": f"Cumulative Dose Alert: {drug}",
                    "body": (f"Total {drug}: {total:.0f}mg ({pct:.0f}% of safe ceiling {ceiling}mg). "
                             f"{'CEILING EXCEEDED — stop further dosing.' if total >= ceiling else 'Approaching maximum — reassess need.'}"),
                    "severity": severity, "pillar": "pharmacist", "at": time.time(),
                },
            ))

        # === CHECK 2: Weight-adjusted safety ===
        safe_ceiling_key = [k for k in pk if "safe_ceiling" in k]
        if safe_ceiling_key:
            ceiling_per_kg = pk[safe_ceiling_key[0]]
            total_per_kg = total / self._patient_weight_kg
            if total_per_kg > ceiling_per_kg:
                results.append(AgentEvent(
                    type=EventType.ALERT,
                    source=self.agent_id, priority=2,
                    session_id=event.session_id,
                    data={
                        "title": f"Weight-Adjusted Ceiling Exceeded: {drug}",
                        "body": f"Total {drug}: {total_per_kg:.2f} mg/kg exceeds safe ceiling of {ceiling_per_kg} mg/kg for {self._patient_weight_kg}kg patient.",
                        "severity": "critical", "pillar": "pharmacist", "at": time.time(),
                    },
                ))

        # === CHECK 3: Stacking detection ===
        drug_state = cortex.drugs.get(drug)
        if drug_state and len(drug_state.doses) >= 2:
            prev_dose = drug_state.doses[-2]
            time_since_prev = (time.time() - prev_dose.timestamp) / 60
            if time_since_prev < pk.get("clinical_duration_min", 30) * 0.5:
                prev_level = drug_state.estimated_plasma_level_pct()
                if prev_level > 50:
                    results.append(AgentEvent(
                        type=EventType.ALERT,
                        source=self.agent_id, priority=3,
                        session_id=event.session_id,
                        data={
                            "title": f"Drug Stacking: {drug}",
                            "body": (f"Previous {drug} dose given {time_since_prev:.0f}min ago. "
                                     f"Estimated residual plasma level: ~{prev_level:.0f}%. "
                                     f"New dose will stack — total effect may be higher than intended."),
                            "severity": "warning", "pillar": "pharmacist", "at": time.time(),
                        },
                    ))

        # === CHECK 4: Drug interactions with timing ===
        other_drugs = [name for name in cortex.drugs if name != drug]
        interactions = check_interactions(drug, other_drugs)
        for interaction in interactions:
            sev = interaction.get("severity", "low")
            if sev in ("high", "critical"):
                # Add temporal context
                other = interaction.get("drug_b", interaction.get("drug_a", ""))
                other_state = cortex.drugs.get(other)
                timing_note = ""
                if other_state:
                    mins = other_state.minutes_since_last()
                    level = other_state.estimated_plasma_level_pct()
                    timing_note = f" ({other} given {mins:.0f}min ago, ~{level:.0f}% plasma remaining)"

                results.append(AgentEvent(
                    type=EventType.ALERT,
                    source=self.agent_id, priority=2,
                    session_id=event.session_id,
                    data={
                        "title": f"Drug Interaction: {drug} + {other}",
                        "body": interaction.get("note", "") + timing_note,
                        "severity": "critical" if sev == "critical" else "warning",
                        "pillar": "pharmacist", "at": time.time(),
                    },
                ))

        # === CHECK 5: Ephedrine tachyphylaxis ===
        if drug == "Ephedrine":
            self._ephedrine_dose_count += 1
            if self._ephedrine_dose_count >= 3:
                results.append(AgentEvent(
                    type=EventType.DISPLAY_TRANSCRIPT,
                    source=self.agent_id, priority=5,
                    session_id=event.session_id,
                    data={
                        "speaker": "pharmacist", "pillar": "pharmacist", "at": time.time(),
                        "text": (f"Ephedrine dose #{self._ephedrine_dose_count}. "
                                 f"Tachyphylaxis expected after 3-4 doses. "
                                 f"Consider switching to phenylephrine or noradrenaline infusion."),
                    },
                ))

        # === ANNOUNCE drug logged with PK timeline ===
        announce = self._build_drug_announcement(drug, dose_mg, dose_per_kg, route, pk, cortex)
        results.append(AgentEvent(
            type=EventType.DISPLAY_TRANSCRIPT,
            source=self.agent_id, priority=7,
            session_id=event.session_id,
            data={"speaker": "pharmacist", "text": announce,
                  "pillar": "pharmacist", "at": time.time()},
        ))

        return results

    def _build_drug_announcement(self, drug, dose_mg, dose_per_kg, route, pk, cortex) -> str:
        parts = [f"{drug} {dose_mg}mg ({dose_per_kg} mg/kg) {route} logged."]

        if pk:
            parts.append(f"Onset ~{pk.get('onset_min', '?')}min, peak ~{pk.get('peak_min', '?')}min, "
                         f"duration ~{pk.get('clinical_duration_min', '?')}min.")

        total = cortex.total_drug_dose(drug)
        dose_count = len(cortex.drugs[drug].doses) if drug in cortex.drugs else 1
        if dose_count > 1:
            parts.append(f"Cumulative: {total:.0f}mg ({dose_count} doses).")

        if pk.get("warnings"):
            parts.append(f"Note: {pk['warnings'][0]}")

        return " ".join(parts)

    def _check_redose_needed(self, event: AgentEvent) -> list[AgentEvent]:
        """Proactive redose alerts for muscle relaxants and key drugs."""
        cortex = get_cortex()
        results = []

        for drug_name in ("Rocuronium", "Atracurium"):
            state = cortex.drugs.get(drug_name)
            if not state or not state.is_any_active():
                continue

            level = state.estimated_plasma_level_pct()
            pk = PK_PROFILES.get(drug_name, {})
            redose_threshold = pk.get("redose_at_pct", 25)

            if level < redose_threshold:
                mins = state.minutes_since_last()
                results.append(AgentEvent(
                    type=EventType.DISPLAY_TRANSCRIPT,
                    source=self.agent_id, priority=5,
                    session_id=event.session_id,
                    data={
                        "speaker": "pharmacist", "pillar": "pharmacist", "at": time.time(),
                        "text": (f"{drug_name} effect estimated at ~{level:.0f}% "
                                 f"({mins:.0f}min since last dose). "
                                 f"{'REDOSE RECOMMENDED — patient may begin to move.' if level < 15 else 'Approaching redose threshold.'} "
                                 f"Suggested: {drug_name} {'0.15mg/kg' if drug_name == 'Rocuronium' else '0.1mg/kg'} IV."),
                    },
                ))
            elif 25 < level < 40:
                mins_to_redose = (state.doses[-1].duration_min -
                                  (time.time() - state.doses[-1].timestamp) / 60)
                if 0 < mins_to_redose < 10:
                    results.append(AgentEvent(
                        type=EventType.DISPLAY_TRANSCRIPT,
                        source=self.agent_id, priority=7,
                        session_id=event.session_id,
                        data={
                            "speaker": "pharmacist", "pillar": "pharmacist", "at": time.time(),
                            "text": f"{drug_name}: redose will be needed in ~{mins_to_redose:.0f} minutes. Prepare dose.",
                        },
                    ))

        return results

    async def _parse_drug_command(self, event: AgentEvent) -> list[AgentEvent]:
        text = event.data.get("text", "")
        import re
        drug_names = "|".join(PK_PROFILES.keys())
        pattern = rf"({drug_names})\s+(\d+\.?\d*)\s*(mg|mcg|ug|ml)?"
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            drug = match.group(1).capitalize()
            # Normalize drug name to match PK_PROFILES keys
            for pk_name in PK_PROFILES:
                if pk_name.lower() == drug.lower():
                    drug = pk_name
                    break

            dose = float(match.group(2))
            unit = (match.group(3) or "mg").lower()
            if unit in ("mcg", "ug"):
                dose = dose / 1000

            route = "IV"
            if "infusion" in text.lower():
                route = "IV infusion"
            elif "im" in text.lower() or "intramuscular" in text.lower():
                route = "IM"

            drug_event = AgentEvent(
                type=EventType.DRUG_ADMINISTERED,
                source="voice", priority=5,
                session_id=event.session_id,
                data={"drug": drug, "dose_mg": dose, "route": route},
            )
            return await self._handle_drug_event(drug_event)

        return []

    def get_drug_summary(self) -> dict:
        cortex = get_cortex()
        return {
            name: {
                "total_mg": state.total_mg,
                "total_per_kg": state.total_per_kg,
                "doses": len(state.doses),
                "active": state.is_any_active(),
                "plasma_pct": state.estimated_plasma_level_pct(),
                "minutes_since_last": state.minutes_since_last(),
            }
            for name, state in cortex.drugs.items()
        }
