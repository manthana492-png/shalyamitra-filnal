"""
ShalyaMitra — Drug Database

Structured database of surgical/anaesthetic drugs with:
  - Standard dosing ranges (per kg and absolute)
  - Drug-drug interactions with severity ratings
  - Contraindications
  - PK parameters for TIVA modelling
  - Reversal agents

Used by: Pharmacist Agent for interaction checking and dosing validation.
"""

from __future__ import annotations
from typing import Optional

# ══════════════════════════════════════════════════════════
# Drug Entries
# ══════════════════════════════════════════════════════════

DRUGS: dict[str, dict] = {
    "Propofol": {
        "class": "Induction agent / Sedative",
        "route": ["IV"],
        "induction_dose_mg_kg": {"min": 1.5, "max": 2.5},
        "maintenance_mcg_kg_min": {"min": 50, "max": 200},
        "onset_seconds": 30,
        "duration_minutes": 8,
        "pk_model": "Marsh / Schnider",
        "contraindications": ["Propofol allergy", "Egg/soy allergy (relative)"],
        "side_effects": ["Hypotension", "Apnoea", "Pain on injection", "Bradycardia"],
        "reversal": None,
        "notes": "Titrate to effect. Reduce dose in elderly, hypovolaemic patients.",
    },
    "Fentanyl": {
        "class": "Opioid analgesic",
        "route": ["IV"],
        "induction_dose_mcg_kg": {"min": 1, "max": 3},
        "maintenance_mcg_kg_hr": {"min": 1, "max": 3},
        "onset_seconds": 60,
        "duration_minutes": 45,
        "pk_model": "Minto",
        "contraindications": ["MAO inhibitor use within 14 days"],
        "side_effects": ["Respiratory depression", "Bradycardia", "Chest wall rigidity", "Nausea"],
        "reversal": "Naloxone 0.1-0.4mg IV",
        "notes": "Context-sensitive half-time increases with prolonged infusion.",
    },
    "Rocuronium": {
        "class": "Non-depolarising neuromuscular blocker",
        "route": ["IV"],
        "intubation_dose_mg_kg": {"min": 0.6, "max": 1.2},
        "maintenance_mg_kg": {"min": 0.1, "max": 0.2},
        "onset_seconds": 60,
        "duration_minutes": 40,
        "pk_model": None,
        "contraindications": ["Myasthenia gravis (relative)"],
        "side_effects": ["Residual paralysis", "Anaphylaxis (rare)"],
        "reversal": "Sugammadex 2-4mg/kg IV or Neostigmine 0.05mg/kg + Glycopyrrolate 0.01mg/kg",
        "notes": "RSI dose: 1.2mg/kg. Monitor with TOF.",
    },
    "Atracurium": {
        "class": "Non-depolarising neuromuscular blocker",
        "route": ["IV"],
        "intubation_dose_mg_kg": {"min": 0.4, "max": 0.5},
        "onset_seconds": 120,
        "duration_minutes": 30,
        "pk_model": None,
        "contraindications": [],
        "side_effects": ["Histamine release", "Bronchospasm", "Hypotension"],
        "reversal": "Neostigmine 0.05mg/kg + Glycopyrrolate 0.01mg/kg",
        "notes": "Hoffman degradation — safe in renal/hepatic failure.",
    },
    "Midazolam": {
        "class": "Benzodiazepine",
        "route": ["IV", "IM", "PO"],
        "premedication_dose_mg": {"min": 1, "max": 5},
        "onset_seconds": 120,
        "duration_minutes": 30,
        "pk_model": None,
        "contraindications": ["Acute narrow-angle glaucoma", "Myasthenia gravis"],
        "side_effects": ["Respiratory depression", "Paradoxical agitation (elderly)"],
        "reversal": "Flumazenil 0.2mg IV, repeat to 1mg",
        "notes": "Reduce dose in elderly. Synergistic with opioids.",
    },
    "Ketamine": {
        "class": "Dissociative anaesthetic / Analgesic",
        "route": ["IV", "IM"],
        "induction_dose_mg_kg": {"min": 1, "max": 2},
        "analgesic_dose_mg_kg": {"min": 0.1, "max": 0.5},
        "onset_seconds": 60,
        "duration_minutes": 15,
        "pk_model": "Domino",
        "contraindications": ["Raised ICP (relative)", "Psychosis history"],
        "side_effects": ["Emergence phenomena", "Hypersalivation", "Hypertension", "Nystagmus"],
        "reversal": None,
        "notes": "Maintains airway reflexes. Useful in haemodynamic instability.",
    },
    "Succinylcholine": {
        "class": "Depolarising neuromuscular blocker",
        "route": ["IV"],
        "dose_mg_kg": {"min": 1, "max": 1.5},
        "onset_seconds": 45,
        "duration_minutes": 8,
        "pk_model": None,
        "contraindications": ["Hyperkalaemia risk", "Burns >24h", "Denervation injury",
                             "Malignant hyperthermia history", "Pseudocholinesterase deficiency"],
        "side_effects": ["Fasciculations", "Hyperkalaemia", "Bradycardia", "Malignant hyperthermia (rare)"],
        "reversal": None,
        "notes": "ONLY for RSI when rocuronium/sugammadex unavailable.",
    },
    "Neostigmine": {
        "class": "Anticholinesterase (reversal agent)",
        "route": ["IV"],
        "dose_mg_kg": {"min": 0.04, "max": 0.07},
        "max_dose_mg": 5,
        "onset_seconds": 300,
        "contraindications": ["Mechanical GI/urinary obstruction"],
        "side_effects": ["Bradycardia", "Bronchospasm", "Increased secretions"],
        "notes": "Always give with glycopyrrolate (0.01mg/kg) or atropine.",
    },
    "Ondansetron": {
        "class": "Antiemetic (5-HT3 antagonist)",
        "route": ["IV"],
        "dose_mg": {"min": 4, "max": 8},
        "onset_seconds": 300,
        "contraindications": ["QT prolongation"],
        "side_effects": ["Headache", "QT prolongation (high dose)"],
        "notes": "Give at end of surgery for PONV prophylaxis.",
    },
    "Dexamethasone": {
        "class": "Corticosteroid / Antiemetic",
        "route": ["IV"],
        "antiemetic_dose_mg": {"min": 4, "max": 8},
        "onset_seconds": 600,
        "contraindications": ["Active infection (relative)", "Uncontrolled diabetes (relative)"],
        "side_effects": ["Hyperglycaemia", "Perineal burning (rapid injection)"],
        "notes": "Give at induction for maximum antiemetic effect.",
    },
    "Ephedrine": {
        "class": "Vasopressor (indirect sympathomimetic)",
        "route": ["IV"],
        "dose_mg": {"min": 3, "max": 12},
        "onset_seconds": 60,
        "duration_minutes": 15,
        "contraindications": ["Severe hypertension"],
        "side_effects": ["Tachycardia", "Hypertension", "Arrhythmias"],
        "notes": "First-line for hypotension with bradycardia. Tachyphylaxis occurs.",
    },
    "Phenylephrine": {
        "class": "Vasopressor (alpha-1 agonist)",
        "route": ["IV"],
        "bolus_mcg": {"min": 50, "max": 200},
        "infusion_mcg_min": {"min": 10, "max": 200},
        "onset_seconds": 30,
        "duration_minutes": 10,
        "contraindications": ["Severe hypertension"],
        "side_effects": ["Reflex bradycardia", "Hypertension"],
        "notes": "Pure alpha. Use when tachycardia accompanies hypotension.",
    },
    "Adrenaline": {
        "class": "Catecholamine / Vasopressor",
        "route": ["IV", "IM", "SC", "ET"],
        "cardiac_arrest_mg": 1,
        "anaphylaxis_mg_im": 0.5,
        "infusion_mcg_kg_min": {"min": 0.01, "max": 0.5},
        "onset_seconds": 10,
        "contraindications": [],
        "side_effects": ["Tachycardia", "Hypertension", "Arrhythmias", "Tremor"],
        "notes": "FIRST-LINE for anaphylaxis (0.5mg IM). Titrate infusion carefully.",
    },
    "Morphine": {
        "class": "Opioid analgesic",
        "route": ["IV", "IM", "SC"],
        "dose_mg_kg": {"min": 0.05, "max": 0.15},
        "onset_seconds": 300,
        "duration_minutes": 240,
        "contraindications": ["Severe asthma (relative)"],
        "side_effects": ["Respiratory depression", "Histamine release", "Nausea", "Pruritis"],
        "reversal": "Naloxone 0.1-0.4mg IV",
        "notes": "Long-acting. Useful for post-op analgesia.",
    },
    "Paracetamol": {
        "class": "Analgesic / Antipyretic",
        "route": ["IV", "PO", "PR"],
        "dose_mg_kg": {"min": 10, "max": 15},
        "max_daily_g": 4,
        "onset_minutes": 15,
        "contraindications": ["Severe hepatic impairment"],
        "side_effects": ["Hepatotoxicity (overdose)"],
        "notes": "Multimodal analgesia cornerstone. Give at induction.",
    },
    "Ketorolac": {
        "class": "NSAID analgesic",
        "route": ["IV", "IM"],
        "dose_mg": {"min": 15, "max": 30},
        "onset_minutes": 10,
        "contraindications": ["Renal impairment", "Active GI bleeding", "Coagulopathy", "Aspirin allergy"],
        "side_effects": ["GI bleeding", "Renal impairment", "Platelet dysfunction"],
        "notes": "Max 2 days parenteral. Avoid in renal patients.",
    },
}

# ══════════════════════════════════════════════════════════
# Drug Interactions Matrix
# ══════════════════════════════════════════════════════════

INTERACTIONS: list[dict] = [
    {"drug_a": "Propofol", "drug_b": "Fentanyl", "severity": "moderate",
     "note": "Synergistic respiratory and cardiovascular depression. Reduce propofol dose by 30-50%."},
    {"drug_a": "Propofol", "drug_b": "Midazolam", "severity": "moderate",
     "note": "Synergistic CNS depression. Reduce propofol induction dose."},
    {"drug_a": "Fentanyl", "drug_b": "Midazolam", "severity": "high",
     "note": "Synergistic respiratory depression. Monitor ventilation closely."},
    {"drug_a": "Succinylcholine", "drug_b": "Neostigmine", "severity": "high",
     "note": "Neostigmine prolongs succinylcholine block. Avoid combination."},
    {"drug_a": "Rocuronium", "drug_b": "Ketamine", "severity": "low",
     "note": "Ketamine may mildly potentiate neuromuscular block."},
    {"drug_a": "Ketorolac", "drug_b": "Adrenaline", "severity": "moderate",
     "note": "NSAIDs may attenuate vasopressor response. Monitor BP."},
    {"drug_a": "Ketorolac", "drug_b": "Morphine", "severity": "low",
     "note": "Complementary analgesic. Reduces opioid requirement by 25-30%."},
    {"drug_a": "Ephedrine", "drug_b": "Adrenaline", "severity": "high",
     "note": "Additive sympathomimetic effect. Risk of severe hypertension/arrhythmia."},
    {"drug_a": "Ondansetron", "drug_b": "Fentanyl", "severity": "low",
     "note": "Minor additive QT prolongation risk. Clinically insignificant at standard doses."},
    {"drug_a": "Atracurium", "drug_b": "Rocuronium", "severity": "moderate",
     "note": "Do not combine different NMBAs. Unpredictable block duration."},
    {"drug_a": "Phenylephrine", "drug_b": "Ephedrine", "severity": "moderate",
     "note": "Additive hypertensive effect. Use one or the other."},
    {"drug_a": "Fentanyl", "drug_b": "Ketamine", "severity": "low",
     "note": "Complementary analgesia. Ketamine reduces opioid tolerance."},
]


def get_drug_db() -> dict[str, dict]:
    """Get the full drug database."""
    return DRUGS


def get_drug_info(drug_name: str) -> Optional[dict]:
    """Get info for a specific drug (case-insensitive)."""
    for name, info in DRUGS.items():
        if name.lower() == drug_name.lower():
            return {"name": name, **info}
    return None


def check_interactions(new_drug: str, existing_drugs: list[str]) -> list[dict]:
    """Check interactions between a new drug and existing drugs."""
    results = []
    new_lower = new_drug.lower()

    for interaction in INTERACTIONS:
        a = interaction["drug_a"].lower()
        b = interaction["drug_b"].lower()

        for existing in existing_drugs:
            ex_lower = existing.lower()
            if (new_lower == a and ex_lower == b) or (new_lower == b and ex_lower == a):
                results.append(interaction)

    return results


def validate_dose(drug_name: str, dose_mg: float, weight_kg: float) -> Optional[dict]:
    """Validate a drug dose against safe ranges."""
    info = get_drug_info(drug_name)
    if not info:
        return None

    dose_per_kg = dose_mg / weight_kg
    warnings = []

    # Check induction dose ranges
    for key in ["induction_dose_mg_kg", "dose_mg_kg", "intubation_dose_mg_kg"]:
        if key in info:
            range_data = info[key]
            if dose_per_kg > range_data["max"] * 1.5:
                warnings.append(f"Dose {dose_per_kg:.1f}mg/kg exceeds maximum ({range_data['max']}mg/kg) by >50%")
            elif dose_per_kg > range_data["max"]:
                warnings.append(f"Dose {dose_per_kg:.1f}mg/kg above standard range ({range_data['min']}-{range_data['max']}mg/kg)")
            elif dose_per_kg < range_data["min"] * 0.5:
                warnings.append(f"Dose {dose_per_kg:.1f}mg/kg may be sub-therapeutic (min: {range_data['min']}mg/kg)")

    return {"drug": drug_name, "dose_mg": dose_mg, "dose_per_kg": round(dose_per_kg, 2),
            "weight_kg": weight_kg, "warnings": warnings, "valid": len(warnings) == 0}
