"""
ShalyaMitra — Complete Marma Database (107 Vital Points)

The canonical database of all 107 Marma points from Suśruta Saṃhitā,
with cross-references to Aṣṭāṅgahṛdayam and Charaka Saṃhitā.

Classification (Suśruta Saṃhitā, Śārīrasthāna 6):
  - Sadya Praṇahara (19): Immediately fatal if injured
  - Kālāntara Praṇahara (33): Fatal over time
  - Viśalyaghna (3): Fatal on removal of foreign body
  - Vaikalyakara (44): Causes disability
  - Rujakara (8): Causes severe pain

Distribution (Suśruta Saṃhitā, Śārīrasthāna 6.2):
  - Śākhā (Extremities): 44 points (11 per limb × 4)
  - Madhya Śarīra (Trunk): 26 points (12 anterior + 14 posterior)
  - Ūrdhva Jatru (Head & Neck): 37 points

Master shloka on Marma definition:
  मर्माणि नाम ते विशेषायतनानि धातूनाम्,
  तेषु स्वभावत एव विशेषेण प्राणास्तिष्ठन्ति।
  — Suśruta Saṃhitā, Śārīrasthāna 6.16

  "Marmas are the special seats of the dhatus (tissues),
   where the vital force (prāṇa) naturally resides in abundance."

Each entry contains:
  - Sanskrit name (Devanagari + transliteration)
  - Suśruta classification and tissue type
  - Precise modern anatomical mapping
  - Relevant shloka with meaning
  - Surgical procedures at risk
  - Protective doctrine for the surgeon
"""

from __future__ import annotations
from typing import Any

from app.knowledge.marma_upper_limb import UPPER_LIMB_MARMAS
from app.knowledge.marma_lower_limb import LOWER_LIMB_MARMAS
from app.knowledge.marma_trunk import TRUNK_MARMAS
from app.knowledge.marma_head_neck import HEAD_NECK_MARMAS
from app.knowledge.marma_supplementary import SUPPLEMENTARY_MARMAS

# ═══════════════════════════════════════════════════════════
# Unified 107 Marma Database
# ═══════════════════════════════════════════════════════════

MARMA_DB: list[dict[str, Any]] = (
    UPPER_LIMB_MARMAS +      # 11 types × bilateral = 22 points
    LOWER_LIMB_MARMAS +      # 11 types × bilateral = 22 points
    TRUNK_MARMAS +           # 12 types (some bilateral) = ~26 points
    HEAD_NECK_MARMAS +       # 14 types (some multiple) = ~37 points
    SUPPLEMENTARY_MARMAS     # Remaining points to reach 107
)

# ═══════════════════════════════════════════════════════════
# Classification Statistics
# ═══════════════════════════════════════════════════════════

CLASSIFICATION_INFO = {
    "Sadya Pranahara": {
        "count": 19,
        "meaning": "Immediately fatal",
        "sanskrit": "सद्यः प्राणहर",
        "description": "Injury causes death immediately or within hours. These overlie major arteries, the heart, or brain centres.",
        "shloka": "सद्यः प्राणहराणि मर्माणि एकोनविंशतिः।",
        "reference": "Suśruta Saṃhitā, Śārīrasthāna 6.9",
    },
    "Kalantara Pranahara": {
        "count": 33,
        "meaning": "Fatal over time (15-30 days)",
        "sanskrit": "कालान्तर प्राणहर",
        "description": "Injury causes death over days to weeks — from infection, delayed haemorrhage, or organ failure.",
        "shloka": "कालान्तरप्राणहराणि त्रयस्त्रिंशत्।",
        "reference": "Suśruta Saṃhitā, Śārīrasthāna 6.10",
    },
    "Vishalyaghna": {
        "count": 3,
        "meaning": "Fatal on removal of foreign body",
        "sanskrit": "विशल्यघ्न",
        "description": "The patient survives while the foreign body (shalya) remains but dies when it is removed — the embedded object is tamponading a critical vessel.",
        "shloka": "विशल्यघ्नानि त्रीणि मर्माणि।",
        "reference": "Suśruta Saṃhitā, Śārīrasthāna 6.11",
    },
    "Vaikalyakara": {
        "count": 44,
        "meaning": "Causes disability / deformity",
        "sanskrit": "वैकल्यकर",
        "description": "Injury causes permanent functional impairment — paralysis, joint stiffness, or loss of function.",
        "shloka": "वैकल्यकराणि चतुश्चत्वारिंशत्।",
        "reference": "Suśruta Saṃhitā, Śārīrasthāna 6.12",
    },
    "Rujakara": {
        "count": 8,
        "meaning": "Causes severe pain",
        "sanskrit": "रुजाकर",
        "description": "Injury causes intense, debilitating pain but is not immediately fatal or permanently disabling.",
        "shloka": "रुजाकराणि अष्टौ मर्माणि।",
        "reference": "Suśruta Saṃhitā, Śārīrasthāna 6.13",
    },
}

TISSUE_TYPES = {
    "Mamsa": {"meaning": "Muscle/flesh", "sanskrit": "मांस"},
    "Sira": {"meaning": "Vessel (vein/artery)", "sanskrit": "सिरा"},
    "Snayu": {"meaning": "Ligament/tendon", "sanskrit": "स्नायु"},
    "Asthi": {"meaning": "Bone", "sanskrit": "अस्थि"},
    "Sandhi": {"meaning": "Joint", "sanskrit": "सन्धि"},
    "Dhamani": {"meaning": "Artery (pulsatile vessel)", "sanskrit": "धमनी"},
}

# ═══════════════════════════════════════════════════════════
# Lookup Functions
# ═══════════════════════════════════════════════════════════

def get_total_point_count() -> int:
    """Get total Marma point count (should be 107)."""
    total = 0
    for m in MARMA_DB:
        total += m.get("count", 1)
    return total


def get_marma_for_procedure(procedure_name: str) -> list[dict[str, Any]]:
    """Get Marma points relevant to a given surgical procedure."""
    procedure_lower = procedure_name.lower()
    relevant = []
    for marma in MARMA_DB:
        for proc in marma.get("procedures_at_risk", []):
            if proc.lower() in procedure_lower or procedure_lower in proc.lower():
                if marma not in relevant:
                    relevant.append(marma)
                break
        for tag in marma.get("surgical_relevance", []):
            if tag in procedure_lower:
                if marma not in relevant:
                    relevant.append(marma)
                break
    return relevant


def get_marma_by_id(marma_id: str) -> dict[str, Any] | None:
    """Get a specific Marma by ID."""
    for marma in MARMA_DB:
        if marma["id"] == marma_id:
            return marma
    return None


def get_marma_by_zone(zone_or_anatomy: str) -> list[dict[str, Any]]:
    """Get Marma points near a given anatomical zone/structure."""
    zone_lower = zone_or_anatomy.lower()
    results = []
    for marma in MARMA_DB:
        searchable = " ".join([
            marma.get("location", ""),
            marma.get("modern_mapping", ""),
            marma.get("zone", ""),
            marma.get("region", ""),
        ]).lower()
        if zone_lower in searchable:
            results.append(marma)
    return results


def get_marma_by_classification(classification: str) -> list[dict[str, Any]]:
    """Get all Marma points of a specific classification."""
    return [m for m in MARMA_DB if m.get("classification", "").lower() == classification.lower()]


def get_marma_by_region(region: str) -> list[dict[str, Any]]:
    """Get all Marma points in a body region."""
    region_lower = region.lower()
    return [m for m in MARMA_DB if region_lower in m.get("region", "").lower()]


def get_critical_marmas() -> list[dict[str, Any]]:
    """Get all Sadya Pranahara (immediately fatal) Marma points."""
    return get_marma_by_classification("Sadya Pranahara")


def get_marma_stats() -> dict:
    """Get summary statistics of the Marma database."""
    total_points = get_total_point_count()
    by_classification = {}
    by_region = {}
    for m in MARMA_DB:
        cls = m.get("classification", "Unknown")
        by_classification[cls] = by_classification.get(cls, 0) + m.get("count", 1)
        reg = m.get("region", "Unknown")
        by_region[reg] = by_region.get(reg, 0) + m.get("count", 1)

    return {
        "total_entries": len(MARMA_DB),
        "total_points": total_points,
        "target": 107,
        "by_classification": by_classification,
        "by_region": by_region,
        "classifications": CLASSIFICATION_INFO,
    }
