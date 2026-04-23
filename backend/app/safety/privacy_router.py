"""
ShalyaMitra — NIM-Powered Inference Router

Three-tier model routing via NVIDIA NIM API (cloud):

  Tier 1: NVIDIA NIM API → Nemotron Super 49B (primary)
  Tier 2: NVIDIA NIM API → Kimi k2.5 (reasoning fallback)
  Tier 3: OpenRouter   → Gemini Flash (final fallback)

Architecture:
  ┌──────────────────────────────────────────────────────────┐
  │                   Privacy Router                         │
  │                                                          │
  │  1. PHI Redaction Engine strips all 17 Indian patterns   │
  │  2. Clean text → NVIDIA NIM API (Tier 1/2/3)            │
  │  3. Every call logged to audit trail                     │
  │  4. No local GPU needed — all via API key               │
  └──────────────────────────────────────────────────────────┘

PHI Safety:
  ALL queries are PHI-stripped BEFORE sending to any cloud endpoint.
  The redaction engine removes: Aadhaar, PAN, ABHA, MRN, names,
  phone numbers, email, dates of birth, etc.

NVIDIA NIM API:
  Base URL: https://integrate.api.nvidia.com/v1
  Auth:     Bearer YOUR_NVIDIA_API_KEY
  Format:   OpenAI-compatible chat completions
  Free:     1,000 calls/month (build.nvidia.com)

Available NIM Models Used:
  - nvidia/llama-3.3-nemotron-super-49b-v1    → Primary reasoning
  - moonshotai/kimi-k2.5                       → Deep thinking
  - nvidia/nemotron-3-nano-30b-a3b             → Fast response
  - nvidia/nemotron-nano-12b-v2-vl             → Vision (surgical field)
  - nvidia/nemotron-content-safety-reasoning-4b → Guardrails
"""

from __future__ import annotations
import re, time, json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional
import httpx

from app.config import settings
from app.safety.phi_redaction import get_phi_engine


class InferenceTier(str, Enum):
    NIM_PRIMARY = "nim_primary"         # Nemotron Super 49B via NIM
    NIM_THINKING = "nim_thinking"       # Kimi k2.5 via NIM
    NIM_FAST = "nim_fast"               # Nemotron Nano 30B via NIM
    NIM_VISION = "nim_vision"           # Nemotron Nano 12B VL via NIM
    OPENROUTER = "openrouter"           # Gemini/Claude via OpenRouter
    FAILED = "failed"


class RouteReason(str, Enum):
    PRIMARY = "nim_primary_call"
    THINKING_REQUIRED = "deep_reasoning_needed"
    FAST_RESPONSE = "low_latency_needed"
    VISION_QUERY = "image_analysis"
    NIM_FALLBACK = "nim_failed_fallback"
    OPENROUTER_FALLBACK = "final_fallback"
    PHI_REDACTED = "phi_stripped_before_cloud"


@dataclass
class RoutingDecision:
    tier: InferenceTier
    reason: RouteReason
    model: str
    endpoint: str
    phi_detected: bool
    phi_redacted: bool
    phi_categories: list[str]
    latency_ms: float = 0.0
    timestamp: float = field(default_factory=time.time)


# Agent → model tier mapping
AGENT_MODEL_MAP = {
    # Clinical agents → Primary reasoning (strongest model)
    "VoiceAgent": "primary",
    "DevilsAdvocateAgent": "primary",
    "MonitorAgent": "fast",          # Needs speed, not deep reasoning
    "HaemorrhageAgent": "fast",      # Speed critical
    "PharmacistAgent": "primary",
    "SentinelAgent": "fast",
    # Knowledge agents → Thinking model (deep reasoning)
    "ScholarAgent": "thinking",
    "ConsultantAgent": "thinking",
    "OracleAgent": "primary",
    "ChroniclerAgent": "primary",
    # Vision agents → Vision model
    "EyeAgent": "vision",
}

# Sensitive keyword patterns for PHI detection
SENSITIVE_PATTERNS = re.compile(
    r'\b(?:patient|MRN|UHID|aadhaar|diagnosis|history|allergy|'
    r'comorbid|medication|blood\s*pressure|heart\s*rate|SpO2|'
    r'operative\s*note|consent|weight|BMI|renal|hepatic|'
    r'Mr\.|Mrs\.|Ms\.|Shri|Smt)\b',
    re.IGNORECASE
)


class PrivacyRouter:
    """
    Three-tier NIM-powered inference router with automatic PHI redaction.

    ALL queries go to cloud (NVIDIA NIM API) — but ALL are PHI-stripped first.
    No local GPU required. No Nemotron 120B. Just an API key.

    Usage:
        router = PrivacyRouter()
        response = await router.infer(messages, agent_type="ScholarAgent")
    """

    def __init__(self):
        self._phi_engine = get_phi_engine()
        self._current_phase: str = "preparation"
        self._force_tier: Optional[str] = None
        self._force_local: bool = False
        self._audit_log: list[RoutingDecision] = []
        self._nim_available: Optional[bool] = None
        self._http: Optional[httpx.AsyncClient] = None

    async def _get_http(self) -> httpx.AsyncClient:
        if self._http is None or self._http.is_closed:
            self._http = httpx.AsyncClient(timeout=30.0)
        return self._http

    def set_phase(self, phase: str):
        self._current_phase = phase.lower()

    def set_force_tier(self, tier: Optional[str]):
        """Force a specific tier: 'primary', 'thinking', 'fast', or None."""
        self._force_tier = tier

    def set_force_local(self, enable: bool):
        """
        Force ALL inference to local GPU only — no data leaves the OR network.

        When enabled, NIM cloud and OpenRouter calls are blocked.
        Used as a surgeon override for maximum data sovereignty.
        In demo mode (no local GPU), this is a no-op with a warning.
        """
        self._force_local = enable
        if enable:
            print("[PRIVACY] Force-local mode ENABLED — all cloud inference blocked")
        else:
            print("[PRIVACY] Force-local mode DISABLED — normal routing resumed")

    def _get_tier_config(self, tier: str) -> tuple[str, str, str]:
        """Returns (model_id, base_url, auth_header) for a tier."""
        if tier == "primary":
            return (settings.nim_reasoning_model,
                    settings.nvidia_nim_base_url,
                    settings.nvidia_api_key)
        elif tier == "thinking":
            return (settings.nim_thinking_model,
                    settings.nvidia_nim_base_url,
                    settings.nvidia_api_key)
        elif tier == "fast":
            return (settings.nim_fast_model,
                    settings.nvidia_nim_base_url,
                    settings.nvidia_api_key)
        elif tier == "vision":
            return (settings.nim_vision_model,
                    settings.nvidia_nim_base_url,
                    settings.nvidia_api_key)
        else:
            # OpenRouter fallback
            return ("google/gemini-2.0-flash-001",
                    settings.openrouter_base_url,
                    settings.openrouter_api_key)

    def _select_tier(self, agent_type: str) -> str:
        """Select the best model tier for this agent."""
        if self._force_tier:
            return self._force_tier
        return AGENT_MODEL_MAP.get(agent_type, "primary")

    async def infer(
        self,
        messages: list[dict],
        agent_type: str = "unknown",
        max_tokens: int = 1024,
        temperature: float = 0.3,
        enable_thinking: bool = False,
    ) -> dict[str, Any]:
        """
        Route and execute an LLM inference request.

        1. Always strip PHI from all messages
        2. Select tier based on agent type
        3. Call NIM API (Tier 1/2/3)
        4. Fall back to OpenRouter if NIM fails
        """
        start_time = time.time()

        # STEP 0: Block cloud calls if force-local mode is active
        if self._force_local:
            return {
                "error": "Force-local mode active — cloud inference blocked for data sovereignty",
                "route": "blocked_local",
            }

        # STEP 1: Always redact PHI before ANY cloud call
        phi_detected = False
        phi_categories = []
        safe_messages = []
        for m in messages:
            if isinstance(m.get("content"), str):
                result = self._phi_engine.redact(m["content"])
                if result.phi_detected:
                    phi_detected = True
                    phi_categories.extend(result.categories_found)
                safe_messages.append({**m, "content": result.redacted_text})
            elif isinstance(m.get("content"), list):
                # Multimodal messages (vision) — redact text parts only
                new_content = []
                for part in m["content"]:
                    if isinstance(part, dict) and part.get("type") == "text":
                        result = self._phi_engine.redact(part["text"])
                        if result.phi_detected:
                            phi_detected = True
                            phi_categories.extend(result.categories_found)
                        new_content.append({"type": "text", "text": result.redacted_text})
                    else:
                        new_content.append(part)
                safe_messages.append({**m, "content": new_content})
            else:
                safe_messages.append(m)

        # STEP 2: Select tier
        tier = self._select_tier(agent_type)

        # Add thinking system prompt for reasoning models
        if enable_thinking and tier in ("primary", "thinking"):
            safe_messages = [{"role": "system", "content": "detailed thinking on"}] + safe_messages

        # STEP 3: Try NIM API (preferred)
        if settings.nvidia_api_key:
            model, base_url, api_key = self._get_tier_config(tier)
            response = await self._call_api(base_url, api_key, model,
                                            safe_messages, max_tokens, temperature,
                                            is_nim=True)
            if response and "error" not in response:
                latency = (time.time() - start_time) * 1000
                self._log_decision(
                    InferenceTier.NIM_PRIMARY if tier == "primary" else
                    InferenceTier.NIM_THINKING if tier == "thinking" else
                    InferenceTier.NIM_FAST if tier == "fast" else
                    InferenceTier.NIM_VISION,
                    RouteReason.PRIMARY if tier == "primary" else
                    RouteReason.THINKING_REQUIRED if tier == "thinking" else
                    RouteReason.FAST_RESPONSE if tier == "fast" else
                    RouteReason.VISION_QUERY,
                    model, base_url, phi_detected, True, phi_categories, latency
                )
                return response

            # NIM failed — try next NIM tier before OpenRouter
            fallback_tiers = ["primary", "fast", "thinking"]
            for fb_tier in fallback_tiers:
                if fb_tier == tier:
                    continue
                fb_model, fb_url, fb_key = self._get_tier_config(fb_tier)
                response = await self._call_api(fb_url, fb_key, fb_model,
                                                safe_messages, max_tokens, temperature,
                                                is_nim=True)
                if response and "error" not in response:
                    latency = (time.time() - start_time) * 1000
                    self._log_decision(InferenceTier.NIM_FAST,
                                       RouteReason.NIM_FALLBACK,
                                       fb_model, fb_url,
                                       phi_detected, True, phi_categories, latency)
                    return response

        # STEP 4: Final fallback — OpenRouter
        if settings.openrouter_api_key:
            or_model, or_url, or_key = self._get_tier_config("openrouter")
            response = await self._call_api(or_url, or_key, or_model,
                                            safe_messages, max_tokens, temperature,
                                            is_nim=False)
            if response and "error" not in response:
                latency = (time.time() - start_time) * 1000
                self._log_decision(InferenceTier.OPENROUTER,
                                   RouteReason.OPENROUTER_FALLBACK,
                                   or_model, or_url,
                                   phi_detected, True, phi_categories, latency)
                return response

        return {"error": "All inference tiers failed", "route": "failed"}

    async def infer_vision(
        self,
        image_b64: str,
        prompt: str,
        agent_type: str = "EyeAgent",
        max_tokens: int = 1024,
    ) -> dict[str, Any]:
        """
        Send an image to NIM Vision model for analysis.
        Used by EyeAgent for surgical field, anatomy, phase detection.
        """
        messages = [{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}},
                {"type": "text", "text": prompt},
            ]
        }]
        return await self.infer(messages, agent_type=agent_type,
                                max_tokens=max_tokens, temperature=0.2)

    async def _call_api(
        self, base_url: str, api_key: str, model: str,
        messages: list[dict], max_tokens: int, temperature: float,
        is_nim: bool = True,
    ) -> Optional[dict]:
        """Call an OpenAI-compatible API endpoint."""
        if not api_key:
            return None
        try:
            http = await self._get_http()
            headers = {"Authorization": f"Bearer {api_key}"}
            if not is_nim:
                headers["HTTP-Referer"] = "https://shalyamitra.dev"
                headers["X-Title"] = "ShalyaMitra"

            resp = await http.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json={
                    "model": model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                },
                timeout=25.0,
            )
            if resp.status_code == 200:
                return resp.json()
            return {"error": f"HTTP {resp.status_code}: {resp.text[:200]}"}
        except Exception as e:
            return {"error": str(e)}

    def _log_decision(self, tier, reason, model, endpoint,
                      phi_detected, phi_redacted, phi_categories, latency):
        self._audit_log.append(RoutingDecision(
            tier=tier, reason=reason, model=model, endpoint=endpoint,
            phi_detected=phi_detected, phi_redacted=phi_redacted,
            phi_categories=list(set(phi_categories)),
            latency_ms=latency,
        ))

    def route(self, text: str, agent_type: str = "unknown") -> RoutingDecision:
        """Lightweight routing decision (for audit/display, not execution)."""
        tier = self._select_tier(agent_type)
        model, base_url, _ = self._get_tier_config(tier)
        phi_result = self._phi_engine.redact(text)
        return RoutingDecision(
            tier=InferenceTier.NIM_PRIMARY if tier == "primary" else InferenceTier.NIM_THINKING,
            reason=RouteReason.PRIMARY,
            model=model, endpoint=base_url,
            phi_detected=phi_result.phi_detected,
            phi_redacted=phi_result.phi_detected,
            phi_categories=phi_result.categories_found if phi_result.phi_detected else [],
        )

    def get_audit_log(self) -> list[dict]:
        return [
            {
                "tier": d.tier.value,
                "reason": d.reason.value,
                "model": d.model,
                "phi_detected": d.phi_detected,
                "phi_redacted": d.phi_redacted,
                "phi_categories": d.phi_categories,
                "latency_ms": round(d.latency_ms, 1),
                "timestamp": d.timestamp,
            }
            for d in self._audit_log
        ]

    def get_stats(self) -> dict:
        total = len(self._audit_log)
        by_tier = {}
        for d in self._audit_log:
            by_tier[d.tier.value] = by_tier.get(d.tier.value, 0) + 1
        by_reason = {}
        for d in self._audit_log:
            by_reason[d.reason.value] = by_reason.get(d.reason.value, 0) + 1
        avg_latency = (sum(d.latency_ms for d in self._audit_log) / total) if total else 0
        phi_redactions = sum(1 for d in self._audit_log if d.phi_redacted)
        return {
            "total_requests": total,
            "by_tier": by_tier,
            "by_reason": by_reason,
            "avg_latency_ms": round(avg_latency, 1),
            "phi_redactions": phi_redactions,
            "current_phase": self._current_phase,
            "nvidia_nim_configured": bool(settings.nvidia_api_key),
            "openrouter_configured": bool(settings.openrouter_api_key),
            "models": {
                "primary": settings.nim_reasoning_model,
                "thinking": settings.nim_thinking_model,
                "fast": settings.nim_fast_model,
                "vision": settings.nim_vision_model,
                "safety": settings.nim_safety_model,
            },
        }


# Singleton
_router: Optional[PrivacyRouter] = None

def get_privacy_router() -> PrivacyRouter:
    global _router
    if _router is None:
        _router = PrivacyRouter()
    return _router
