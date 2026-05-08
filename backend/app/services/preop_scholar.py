"""
Scholar-backed structured pre-operative analysis (REST /preop/analyse).

Uses OpenRouter + optional RAG context; falls back to deterministic mock-shaped JSON if offline.
"""

from __future__ import annotations

import json
import re
from typing import Any, Optional

import httpx

from app.config import settings
from app.knowledge.rag_pipeline import RAGPipeline
from app.models.schemas import PreOpAnalysis


class PreopGenerationError(RuntimeError):
    """Raised when structured pre-op generation cannot complete."""


def _extract_json_block(text: str) -> Optional[dict[str, Any]]:
    if not text:
        return None
    s = text.strip()
    if s.startswith("```"):
        s = re.sub(r"^```\w*\n?", "", s)
        s = re.sub(r"\n?```\s*$", "", s)
    try:
        return json.loads(s)
    except Exception:
        pass
    m = re.search(r"\{[\s\S]*\}", s)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except Exception:
        return None


def _demo_shape(session_id: str, procedure: str) -> PreOpAnalysis:
    """Shape-compatible fallback used only in explicit demo mode."""
    return PreOpAnalysis(
        session_id=session_id,
        clinical_synthesis=(
            f"Pre-operative synthesis for {procedure}. "
            "Cloud Scholar offline — display fallback narrative only."
        ),
        risk_flags=[
            {"severity": "info", "text": "Scholar LLM unavailable — verify OPENROUTER_API_KEY"},
        ],
        drug_interactions=[],
        asa_score=2,
        rcri_score=1,
        anatomical_deviations=["Pending structured imaging review"],
        ayurvedic_assessment={
            "prakriti": "pending",
            "dosha_disturbance": "pending",
            "agni_status": "pending",
        },
        marma_zones=[],
    )


async def generate_preop_analysis(
    session_id: str,
    session_meta: Optional[dict[str, Any]] = None,
) -> PreOpAnalysis:
    """Build PreOpAnalysis via Scholar-style LLM prompt (+ RAG)."""
    meta = session_meta or {}
    procedure = meta.get("procedure_name") or meta.get("procedure") or "Elective laparoscopic procedure"
    patient_ctx = {
        "name": meta.get("patient_name"),
        "age": meta.get("patient_age"),
        "weight_kg": meta.get("patient_weight_kg"),
        "bmi": meta.get("patient_bmi"),
        "asa_grade": meta.get("asa_grade"),
        "comorbidities": meta.get("comorbidities"),
    }

    rag = RAGPipeline()
    lit = await rag.query(f"preoperative risk {procedure} complications", top_k=3)
    lit_context = "\n".join(r.get("text", "") for r in lit) if lit else ""

    prompt = f"""You are The Scholar (ShalyaMitra). Produce a MASTER pre-operative analysis as JSON ONLY.

Procedure: {procedure}
Patient snapshot: {json.dumps(patient_ctx, ensure_ascii=False)}
Literature snippets:
{lit_context}

Return JSON with EXACTLY these keys:
{{
  "clinical_synthesis": "<string, 2-4 sentences>",
  "risk_flags": [{{"severity": "warning|caution|info", "text": "<string>"}}],
  "drug_interactions": [{{"drugs": ["A","B"], "severity": "low|moderate|high", "note": "<string>"}}],
  "asa_score": <int 1-5>,
  "rcri_score": <int 0-6>,
  "anatomical_deviations": ["<string>", ...],
  "ayurvedic_assessment": {{
    "prakriti": "<string>",
    "dosha_disturbance": "<string>",
    "agni_status": "<string>"
  }},
  "marma_zones": [
    {{"name": "<string>", "devanagari": "<string>", "zone": "<string>",
      "risk": "Low|Moderate|High", "note": "<string>"}}
  ]
}}
No markdown, no commentary — JSON object only."""

    raw_text: Optional[str] = None
    if settings.openrouter_api_key:
        try:
            async with httpx.AsyncClient(timeout=45.0) as http:
                resp = await http.post(
                    f"{settings.openrouter_base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.openrouter_api_key}",
                        "HTTP-Referer": "https://shalyamitra.quaasx108.com",
                        "X-Title": "ShalyaMitra PreOp Scholar",
                    },
                    json={
                        "model": settings.scholar_model,
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 1200,
                        "temperature": 0.15,
                    },
                )
                if resp.status_code == 200:
                    raw_text = resp.json()["choices"][0]["message"]["content"].strip()
        except Exception:
            raw_text = None

    blob = _extract_json_block(raw_text or "")
    if not blob:
        if settings.demo_mode:
            return _demo_shape(session_id, procedure)
        raise PreopGenerationError(
            "Structured pre-op analysis unavailable (Scholar response missing/invalid JSON)"
        )

    try:
        return PreOpAnalysis(
            session_id=session_id,
            clinical_synthesis=str(blob.get("clinical_synthesis") or ""),
            risk_flags=list(blob.get("risk_flags") or []),
            drug_interactions=list(blob.get("drug_interactions") or []),
            asa_score=int(blob.get("asa_score") or 2),
            rcri_score=int(blob.get("rcri_score") or 0),
            anatomical_deviations=list(blob.get("anatomical_deviations") or []),
            ayurvedic_assessment=dict(blob.get("ayurvedic_assessment") or {}),
            marma_zones=list(blob.get("marma_zones") or []),
        )
    except Exception:
        if settings.demo_mode:
            return _demo_shape(session_id, procedure)
        raise PreopGenerationError("Structured pre-op analysis parse failure")
