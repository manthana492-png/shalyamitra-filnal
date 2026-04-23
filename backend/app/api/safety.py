"""
ShalyaMitra — Safety API

REST endpoints for PHI redaction and clinical guardrails:
  - Redact PHI from any text
  - Check text through clinical guardrails
  - Get audit logs and statistics
  - Configure redaction mode
"""
from __future__ import annotations
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.auth.jwt import get_current_user, AuthUser
from app.safety.phi_redaction import get_phi_engine, get_phi_middleware, RedactionMode
from app.safety.clinical_guardrails import get_guardrails_engine
from app.safety.privacy_router import get_privacy_router

router = APIRouter()


class RedactRequest(BaseModel):
    text: str
    mode: str = "mask"   # mask | hash | partial


class GuardrailCheckRequest(BaseModel):
    text: str
    agent_type: str = "manual"


@router.post("/phi/redact")
async def redact_phi(
    body: RedactRequest,
    user: AuthUser = Depends(get_current_user),
):
    """Redact PHI/PII from text. Returns redacted text + detected categories."""
    mode = RedactionMode(body.mode) if body.mode in [m.value for m in RedactionMode] else RedactionMode.MASK
    engine = get_phi_engine(mode=mode)
    result = engine.redact(body.text)
    return {
        "redacted_text": result.redacted_text,
        "phi_detected": result.phi_detected,
        "categories_found": result.categories_found,
        "match_count": len(result.matches),
        "processing_ms": round(result.processing_time_ms, 2),
    }


@router.post("/guardrails/check")
async def check_guardrails(
    body: GuardrailCheckRequest,
    user: AuthUser = Depends(get_current_user),
):
    """Run clinical guardrails on text. Returns safe version + violations."""
    engine = get_guardrails_engine()
    result = await engine.check(body.text, agent_type=body.agent_type)
    return {
        "safe_text": result.safe_text,
        "outcome": result.outcome.value,
        "violations": [
            {"rule": v.rule_name, "severity": v.severity, "category": v.category.value}
            for v in result.violations
        ],
        "caveats_added": result.caveats_added,
        "llm_validated": result.llm_validated,
        "processing_ms": round(result.processing_time_ms, 2),
    }


@router.get("/phi/stats")
async def phi_stats(user: AuthUser = Depends(get_current_user)):
    """Get PHI detection statistics and audit log summary."""
    middleware = get_phi_middleware()
    return middleware.get_stats()


@router.get("/guardrails/stats")
async def guardrails_stats(user: AuthUser = Depends(get_current_user)):
    """Get guardrails trigger statistics and audit log summary."""
    engine = get_guardrails_engine()
    return engine.get_stats()


@router.get("/guardrails/audit")
async def guardrails_audit(user: AuthUser = Depends(get_current_user)):
    """Get the full guardrails audit log (admin use)."""
    engine = get_guardrails_engine()
    return {"audit_log": engine.get_audit_log()}


# ── Privacy Router (NemoClaw) ─────────────────────────────

@router.get("/privacy/stats")
async def privacy_stats(user: AuthUser = Depends(get_current_user)):
    """Get privacy routing statistics — local vs cloud inference split."""
    router_inst = get_privacy_router()
    return router_inst.get_stats()


@router.get("/privacy/audit")
async def privacy_audit(user: AuthUser = Depends(get_current_user)):
    """Get the privacy routing audit log — every routing decision."""
    router_inst = get_privacy_router()
    return {"audit_log": router_inst.get_audit_log()}


@router.post("/privacy/force-local")
async def force_local_mode(
    enable: bool = True,
    user: AuthUser = Depends(get_current_user),
):
    """Force ALL inference to local GPU (surgeon override). No data leaves OR."""
    router_inst = get_privacy_router()
    router_inst.set_force_local(enable)
    return {"force_local": enable, "status": "All traffic now routed to local GPU" if enable else "Normal routing resumed"}

