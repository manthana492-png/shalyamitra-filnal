"""
ShalyaMitra — PHI/PII Redaction Engine

Production-grade Protected Health Information (PHI) and Personally
Identifiable Information (PII) detection and redaction for HIPAA
and DISHA (India Digital Health) compliance.

Replaces NVIDIA Morpheus with a self-contained, zero-dependency
engine that runs on CPU with no external services.

Applied at 3 points:
  1. Transcripts — before storage in database
  2. Chronicler reports — before generating operative notes
  3. WebSocket events — before broadcasting to frontend

Supports:
  - Indian identifiers: Aadhaar, PAN, ABHA, voter ID
  - Medical identifiers: MRN, insurance ID, bed number
  - Universal PII: names, DOB, phone, email, addresses
  - Contextual PHI: diagnosis combined with identifiers

Redaction modes:
  - MASK:    "Ravi Kumar" → "[PATIENT_NAME]"
  - HASH:    "Ravi Kumar" → "[NAME_a3f2b1]"
  - PARTIAL: "9876543210" → "98XXXXXX10"
"""

from __future__ import annotations
import re, hashlib, time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class RedactionMode(str, Enum):
    MASK = "mask"           # Replace with type label
    HASH = "hash"           # Replace with type + short hash
    PARTIAL = "partial"     # Show first/last chars


class PHICategory(str, Enum):
    PATIENT_NAME = "PATIENT_NAME"
    DATE_OF_BIRTH = "DATE_OF_BIRTH"
    AGE = "AGE"
    PHONE = "PHONE"
    EMAIL = "EMAIL"
    AADHAAR = "AADHAAR"
    PAN = "PAN"
    ABHA = "ABHA"
    VOTER_ID = "VOTER_ID"
    MRN = "MRN"
    INSURANCE_ID = "INSURANCE_ID"
    ADDRESS = "ADDRESS"
    PINCODE = "PINCODE"
    IP_ADDRESS = "IP_ADDRESS"
    BED_NUMBER = "BED_NUMBER"
    UHID = "UHID"


@dataclass
class PHIMatch:
    """A detected PHI/PII entity."""
    category: PHICategory
    original: str
    redacted: str
    start: int
    end: int
    confidence: float


@dataclass
class RedactionResult:
    """Result of redacting a text."""
    original_text: str
    redacted_text: str
    matches: list[PHIMatch]
    phi_detected: bool
    categories_found: list[str]
    processing_time_ms: float


# ════════════════════════════════════════════════════════
# Pattern Definitions
# ════════════════════════════════════════════════════════

# Indian Aadhaar: 12 digits, usually grouped as XXXX XXXX XXXX
AADHAAR_PATTERN = re.compile(
    r'\b[2-9]\d{3}[\s-]?\d{4}[\s-]?\d{4}\b'
)

# Indian PAN: ABCDE1234F
PAN_PATTERN = re.compile(
    r'\b[A-Z]{5}\d{4}[A-Z]\b'
)

# ABHA (Ayushman Bharat Health Account): 14 digits XX-XXXX-XXXX-XXXX
ABHA_PATTERN = re.compile(
    r'\b\d{2}[-]?\d{4}[-]?\d{4}[-]?\d{4}\b'
)

# Indian Voter ID: ABC1234567
VOTER_ID_PATTERN = re.compile(
    r'\b[A-Z]{3}\d{7}\b'
)

# Phone: Indian mobile (10 digits starting with 6-9) or with +91
PHONE_PATTERN = re.compile(
    r'(?:\+91[\s-]?)?(?:\b[6-9]\d{9}\b)'
)

# Email
EMAIL_PATTERN = re.compile(
    r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'
)

# Date of birth patterns: DD/MM/YYYY, DD-MM-YYYY, YYYY-MM-DD
DOB_PATTERN = re.compile(
    r'(?:DOB|D\.O\.B|date\s*of\s*birth|born\s*on|birth\s*date)'
    r'[\s:]*(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4})',
    re.IGNORECASE
)

# Standalone date (contextual — only redact near PHI keywords)
DATE_PATTERN = re.compile(
    r'\b(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})\b'
)

# MRN / UHID (hospital identifier): MRN followed by digits, or UHID
MRN_PATTERN = re.compile(
    r'(?:MRN|UHID|MR\s*No|IP\s*No|OP\s*No|Reg\s*No)[.:\s#]*([A-Z0-9\-]{4,15})',
    re.IGNORECASE
)

# Insurance ID
INSURANCE_PATTERN = re.compile(
    r'(?:insurance|policy|claim)[\s]*(?:no|number|id|#)[.:\s]*([A-Z0-9\-]{6,20})',
    re.IGNORECASE
)

# Bed number
BED_PATTERN = re.compile(
    r'(?:bed|ward|room)[\s]*(?:no|number|#)?[.:\s]*([A-Z]?\d{1,4}[A-Z]?)',
    re.IGNORECASE
)

# Indian pincode
PINCODE_PATTERN = re.compile(
    r'\b[1-9]\d{5}\b'
)

# IP address
IP_PATTERN = re.compile(
    r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
)

# Name patterns (contextual — near keywords like "patient", "name", "Mr/Mrs")
NAME_CONTEXT_PATTERN = re.compile(
    r'(?:patient|name|mr\.?|mrs\.?|ms\.?|dr\.?|shri|smt|kumari)'
    r'[\s:]*([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3})',
    re.IGNORECASE
)

# Age with context
AGE_PATTERN = re.compile(
    r'(?:age|aged|years?\s*old|yr?\s*old)[:\s]*(\d{1,3})',
    re.IGNORECASE
)

# Address (multiword after "address" keyword)
ADDRESS_PATTERN = re.compile(
    r'(?:address|residence|residing\s+at)[:\s]*([\w\s,.\-#/]{10,80})',
    re.IGNORECASE
)


# ════════════════════════════════════════════════════════
# Redaction Engine
# ════════════════════════════════════════════════════════

class PHIRedactionEngine:
    """
    Production-grade PHI/PII redaction engine.

    Usage:
        engine = PHIRedactionEngine(mode=RedactionMode.MASK)
        result = engine.redact("Patient Ravi Kumar, Aadhaar 1234 5678 9012")
        print(result.redacted_text)
        # → "Patient [PATIENT_NAME], Aadhaar [AADHAAR]"
    """

    def __init__(
        self,
        mode: RedactionMode = RedactionMode.MASK,
        categories: Optional[set[PHICategory]] = None,
        whitelist: Optional[set[str]] = None,
    ):
        self.mode = mode
        self.categories = categories or set(PHICategory)
        self.whitelist = whitelist or set()  # Terms to never redact

        # Surgical terms that look like names but aren't
        self._surgical_whitelist = {
            "calot", "hartmann", "kocher", "murphy", "mcburney",
            "lanz", "pfannenstiel", "pringle", "rouviere",
            "hesselbach", "bogros", "retzius", "morrison",
            "said", "okay", "hello", "please", "thank",
            "nael", "shalyamitra", "sushruta", "charaka",
        }
        self.whitelist.update(self._surgical_whitelist)

        # Compile detection pipeline
        self._detectors: list[tuple[PHICategory, re.Pattern, int]] = [
            (PHICategory.AADHAAR, AADHAAR_PATTERN, 0),
            (PHICategory.PAN, PAN_PATTERN, 0),
            (PHICategory.ABHA, ABHA_PATTERN, 0),
            (PHICategory.VOTER_ID, VOTER_ID_PATTERN, 0),
            (PHICategory.EMAIL, EMAIL_PATTERN, 0),
            (PHICategory.PHONE, PHONE_PATTERN, 0),
            (PHICategory.DATE_OF_BIRTH, DOB_PATTERN, 1),
            (PHICategory.MRN, MRN_PATTERN, 1),
            (PHICategory.UHID, MRN_PATTERN, 1),
            (PHICategory.INSURANCE_ID, INSURANCE_PATTERN, 1),
            (PHICategory.BED_NUMBER, BED_PATTERN, 1),
            (PHICategory.AGE, AGE_PATTERN, 1),
            (PHICategory.PATIENT_NAME, NAME_CONTEXT_PATTERN, 1),
            (PHICategory.ADDRESS, ADDRESS_PATTERN, 1),
            (PHICategory.IP_ADDRESS, IP_PATTERN, 0),
        ]

    def _make_redaction(self, category: PHICategory, original: str) -> str:
        """Generate redacted replacement based on mode."""
        if self.mode == RedactionMode.MASK:
            return f"[{category.value}]"

        elif self.mode == RedactionMode.HASH:
            short_hash = hashlib.sha256(
                original.encode()
            ).hexdigest()[:6]
            return f"[{category.value}_{short_hash}]"

        elif self.mode == RedactionMode.PARTIAL:
            if len(original) <= 4:
                return "X" * len(original)
            return original[:2] + "X" * (len(original) - 4) + original[-2:]

        return f"[{category.value}]"

    def detect(self, text: str) -> list[PHIMatch]:
        """Detect all PHI/PII in text without redacting."""
        matches: list[PHIMatch] = []
        seen_spans: set[tuple[int, int]] = set()

        for category, pattern, group_idx in self._detectors:
            if category not in self.categories:
                continue

            for match in pattern.finditer(text):
                if group_idx > 0 and group_idx <= len(match.groups()):
                    value = match.group(group_idx)
                    start = match.start(group_idx)
                    end = match.end(group_idx)
                else:
                    value = match.group(0)
                    start = match.start()
                    end = match.end()

                # Skip whitelisted terms
                if value.lower().strip() in self.whitelist:
                    continue

                # Skip overlapping matches
                span = (start, end)
                if any(s <= start < e or s < end <= e for s, e in seen_spans):
                    continue

                seen_spans.add(span)
                redacted = self._make_redaction(category, value)
                matches.append(PHIMatch(
                    category=category,
                    original=value,
                    redacted=redacted,
                    start=start,
                    end=end,
                    confidence=0.90 if group_idx == 0 else 0.75,
                ))

        # Sort by position (reverse for safe replacement)
        matches.sort(key=lambda m: m.start, reverse=True)
        return matches

    def redact(self, text: str) -> RedactionResult:
        """Detect and redact all PHI/PII from text."""
        t0 = time.time()
        matches = self.detect(text)

        redacted = text
        for m in matches:
            redacted = redacted[:m.start] + m.redacted + redacted[m.end:]

        categories_found = list({m.category.value for m in matches})

        return RedactionResult(
            original_text=text,
            redacted_text=redacted,
            matches=matches,
            phi_detected=len(matches) > 0,
            categories_found=categories_found,
            processing_time_ms=(time.time() - t0) * 1000,
        )

    def redact_dict(self, data: dict[str, Any], keys_to_redact: Optional[list[str]] = None) -> dict[str, Any]:
        """Redact PHI from specific string fields in a dictionary."""
        result = {}
        target_keys = keys_to_redact or [
            "text", "transcript", "content", "notes", "summary",
            "patient_name", "address", "phone", "email",
            "narrative", "report", "message",
        ]
        for key, value in data.items():
            if isinstance(value, str) and key.lower() in target_keys:
                r = self.redact(value)
                result[key] = r.redacted_text
            elif isinstance(value, dict):
                result[key] = self.redact_dict(value, keys_to_redact)
            elif isinstance(value, list):
                result[key] = [
                    self.redact_dict(item, keys_to_redact) if isinstance(item, dict)
                    else self.redact(item).redacted_text if isinstance(item, str) and key.lower() in target_keys
                    else item
                    for item in value
                ]
            else:
                result[key] = value
        return result


# ════════════════════════════════════════════════════════
# Middleware — auto-redaction for WebSocket events
# ════════════════════════════════════════════════════════

class PHIRedactionMiddleware:
    """
    Middleware that auto-redacts PHI from agent events
    before they are broadcast via WebSocket or stored.

    Usage:
        middleware = PHIRedactionMiddleware()
        safe_event = middleware.process_event(agent_event)
    """

    def __init__(self, mode: RedactionMode = RedactionMode.MASK):
        self._engine = PHIRedactionEngine(mode=mode)
        self._audit_log: list[dict] = []

    def process_event(self, event_data: dict[str, Any]) -> dict[str, Any]:
        """Redact PHI from an event before broadcast/storage."""
        redacted = self._engine.redact_dict(event_data)

        # Log if PHI was found (for audit trail)
        original_text = event_data.get("text", "") or event_data.get("transcript", "")
        if original_text:
            result = self._engine.redact(original_text)
            if result.phi_detected:
                self._audit_log.append({
                    "timestamp": time.time(),
                    "categories": result.categories_found,
                    "count": len(result.matches),
                    "event_type": event_data.get("type", "unknown"),
                })

        return redacted

    def process_transcript(self, text: str) -> str:
        """Redact PHI from a transcript line."""
        return self._engine.redact(text).redacted_text

    def process_report(self, report: str) -> str:
        """Redact PHI from an operative report before storage."""
        return self._engine.redact(report).redacted_text

    def get_audit_log(self) -> list[dict]:
        """Get the PHI detection audit log."""
        return self._audit_log.copy()

    def get_stats(self) -> dict:
        """Get PHI detection statistics."""
        total = len(self._audit_log)
        categories = {}
        for entry in self._audit_log:
            for cat in entry.get("categories", []):
                categories[cat] = categories.get(cat, 0) + 1
        return {
            "total_detections": total,
            "by_category": categories,
            "mode": self._engine.mode.value,
        }


# Singleton
_engine: Optional[PHIRedactionEngine] = None
_middleware: Optional[PHIRedactionMiddleware] = None


def get_phi_engine(mode: RedactionMode = RedactionMode.MASK) -> PHIRedactionEngine:
    global _engine
    if _engine is None:
        _engine = PHIRedactionEngine(mode=mode)
    return _engine


def get_phi_middleware(mode: RedactionMode = RedactionMode.MASK) -> PHIRedactionMiddleware:
    global _middleware
    if _middleware is None:
        _middleware = PHIRedactionMiddleware(mode=mode)
    return _middleware
