"""
ShalyaMitra — Voice Profile Manager

Manages the library of TTS voice profiles for Fish Speech 1.5.
Each profile is a short reference audio clip (~10-30s) that Fish Speech
uses to clone the voice characteristics for synthesis.

Voice selection hierarchy:
  1. Safety override: Critical alerts ALWAYS use the urgent alert voice
  2. Pillar voice: Oracle, Pharmacist, Monitor have distinct voices
  3. Surgeon preference: The conversational Nael voice is user-selectable
  4. Default: Calm professional voice

Storage:
  - Built-in voices: shipped in /app/voices/ directory
  - Custom voices: uploaded by surgeon → stored in MinIO under voices/{user_id}/
"""

from __future__ import annotations

import base64
import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

from app.config import settings


class VoiceCategory(str, Enum):
    """Voice categories — safety voices cannot be overridden."""
    SAFETY = "safety"           # Critical alerts — locked, not selectable
    PILLAR = "pillar"           # Pillar-specific voices (Oracle, Pharmacist, etc.)
    CONVERSATIONAL = "conversational"  # Nael's main voice — surgeon-selectable
    CUSTOM = "custom"           # Surgeon-uploaded custom voice


@dataclass
class VoiceProfile:
    """A single voice profile with metadata."""
    id: str
    name: str
    description: str
    category: VoiceCategory
    pillar: Optional[str] = None        # Which pillar this voice is for (if pillar-specific)
    reference_path: Optional[str] = None  # Path to reference .wav file
    reference_b64: Optional[str] = None   # Cached base64 of reference audio
    language: str = "en"
    gender: str = "neutral"
    is_default: bool = False
    selectable: bool = True             # Can surgeon select this for conversational?


# ══════════════════════════════════════════════════════════
# Built-in Voice Profiles
# ══════════════════════════════════════════════════════════

BUILTIN_VOICES: dict[str, VoiceProfile] = {
    # ── Safety Voices (NOT selectable, used for critical alerts) ──
    "alert_urgent": VoiceProfile(
        id="alert_urgent",
        name="Alert — Urgent",
        description="Firm, urgent tone for critical safety alerts. Used by Haemorrhage Sentinel.",
        category=VoiceCategory.SAFETY,
        gender="neutral",
        selectable=False,
    ),
    "alert_warning": VoiceProfile(
        id="alert_warning",
        name="Alert — Warning",
        description="Measured but firm tone for warning-level alerts.",
        category=VoiceCategory.SAFETY,
        gender="neutral",
        selectable=False,
    ),

    # ── Pillar Voices ────────────────────────────────────
    "oracle": VoiceProfile(
        id="oracle",
        name="The Oracle",
        description="Deep, measured, scholarly voice for Ayurvedic wisdom and Marma advisories.",
        category=VoiceCategory.PILLAR,
        pillar="oracle",
        gender="male",
        selectable=False,
    ),
    "pharmacist": VoiceProfile(
        id="pharmacist",
        name="The Pharmacist",
        description="Clinical, precise, matter-of-fact tone for drug logs and PK updates.",
        category=VoiceCategory.PILLAR,
        pillar="pharmacist",
        gender="neutral",
        selectable=False,
    ),
    "monitor": VoiceProfile(
        id="monitor",
        name="Monitor Sentinel",
        description="Neutral, status-report style voice for vital sign announcements.",
        category=VoiceCategory.PILLAR,
        pillar="monitor",
        gender="neutral",
        selectable=False,
    ),

    # ── Conversational Voices (surgeon-selectable) ───────
    "nael_calm": VoiceProfile(
        id="nael_calm",
        name="Nael — Calm",
        description="Default. Calm, composed, warm professional voice.",
        category=VoiceCategory.CONVERSATIONAL,
        gender="neutral",
        is_default=True,
        selectable=True,
    ),
    "nael_female_pro": VoiceProfile(
        id="nael_female_pro",
        name="Nael — Professional Female",
        description="Clear, confident female voice with clinical precision.",
        category=VoiceCategory.CONVERSATIONAL,
        gender="female",
        selectable=True,
    ),
    "nael_male_pro": VoiceProfile(
        id="nael_male_pro",
        name="Nael — Professional Male",
        description="Steady, authoritative male voice.",
        category=VoiceCategory.CONVERSATIONAL,
        gender="male",
        selectable=True,
    ),
    "nael_warm": VoiceProfile(
        id="nael_warm",
        name="Nael — Warm Companion",
        description="Softer, empathetic voice with a reassuring quality.",
        category=VoiceCategory.CONVERSATIONAL,
        gender="neutral",
        selectable=True,
    ),
    "nael_classical": VoiceProfile(
        id="nael_classical",
        name="Nael — Classical",
        description="Deeper, measured, Oracle-inspired voice for the scholarly surgeon.",
        category=VoiceCategory.CONVERSATIONAL,
        gender="male",
        selectable=True,
    ),
}


class VoiceProfileManager:
    """
    Manages voice profiles for the current surgery session.

    At session start:
      1. Loads surgeon's voice preference from profile
      2. Caches all reference audio in memory (base64)
      3. Provides voice resolution: (pillar, severity) → VoiceProfile
    """

    def __init__(self):
        self.profiles: dict[str, VoiceProfile] = dict(BUILTIN_VOICES)
        self.surgeon_preference: str = "nael_calm"  # Default
        self._reference_cache: dict[str, str] = {}  # voice_id → base64 audio

    def set_surgeon_preference(self, voice_id: str):
        """Set the surgeon's preferred conversational voice."""
        if voice_id in self.profiles and self.profiles[voice_id].selectable:
            self.surgeon_preference = voice_id
        else:
            self.surgeon_preference = "nael_calm"

    def add_custom_voice(self, voice_id: str, name: str, description: str,
                         reference_audio_b64: str, user_id: str):
        """Add a surgeon-uploaded custom voice profile."""
        profile = VoiceProfile(
            id=voice_id,
            name=name,
            description=description,
            category=VoiceCategory.CUSTOM,
            reference_b64=reference_audio_b64,
            selectable=True,
        )
        self.profiles[voice_id] = profile
        self._reference_cache[voice_id] = reference_audio_b64

    def resolve_voice(self, pillar: str, severity: str = "info") -> VoiceProfile:
        """
        Resolve the correct voice profile for a given context.

        Priority:
          1. Critical/warning severity → safety alert voice (LOCKED)
          2. Pillar-specific voice (oracle, pharmacist, monitor)
          3. Surgeon's preferred conversational voice
          4. Default (nael_calm)
        """
        # Rule 1: Safety override — critical alerts use fixed voice
        if severity == "critical":
            return self.profiles["alert_urgent"]
        if severity == "warning":
            return self.profiles["alert_warning"]

        # Rule 2: Pillar-specific voice
        pillar_voices = {
            "oracle": "oracle",
            "pharmacist": "pharmacist",
            "monitor": "monitor",
        }
        if pillar in pillar_voices:
            return self.profiles[pillar_voices[pillar]]

        # Rule 3: Surgeon's preference
        if self.surgeon_preference in self.profiles:
            return self.profiles[self.surgeon_preference]

        # Rule 4: Default
        return self.profiles["nael_calm"]

    def get_selectable_voices(self) -> list[dict]:
        """Get all voices the surgeon can choose from (for the settings UI)."""
        return [
            {
                "id": v.id,
                "name": v.name,
                "description": v.description,
                "gender": v.gender,
                "category": v.category.value,
                "is_default": v.is_default,
            }
            for v in self.profiles.values()
            if v.selectable
        ]

    def get_reference_audio(self, voice_id: str) -> Optional[str]:
        """Get the base64-encoded reference audio for a voice profile."""
        if voice_id in self._reference_cache:
            return self._reference_cache[voice_id]

        profile = self.profiles.get(voice_id)
        if not profile or not profile.reference_path:
            return None

        # Load from disk
        path = Path(profile.reference_path)
        if path.exists():
            audio_bytes = path.read_bytes()
            b64 = base64.b64encode(audio_bytes).decode("utf-8")
            self._reference_cache[voice_id] = b64
            return b64

        return None


# Singleton
_manager: Optional[VoiceProfileManager] = None


def get_voice_manager() -> VoiceProfileManager:
    global _manager
    if _manager is None:
        _manager = VoiceProfileManager()
    return _manager
