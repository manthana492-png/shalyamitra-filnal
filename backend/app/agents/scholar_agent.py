"""
ShalyaMitra — Scholar Agent (The Scholar)

Pre-operative intelligence: analyses patient history, imaging, labs,
and generates a structured surgical brief with risk stratification.

Uses: OpenRouter LLM (Claude/Gemini) + RAG over medical literature.
"""

from __future__ import annotations
from typing import Any, Optional
import httpx, time
from app.agents.orchestrator import BaseAgent, AgentEvent, EventType
from app.config import settings
from app.knowledge.rag_pipeline import RAGPipeline


class ScholarAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_id="scholar", pillar="scholar")
        self._http: Optional[httpx.AsyncClient] = None

    @property
    def subscriptions(self) -> list[EventType]:
        return [EventType.SESSION_START, EventType.TRANSCRIPT]

    async def _get_http(self) -> httpx.AsyncClient:
        if self._http is None or self._http.is_closed:
            self._http = httpx.AsyncClient(timeout=30.0)
        return self._http

    async def handle_event(self, event: AgentEvent) -> list[AgentEvent]:
        if event.type == EventType.SESSION_START:
            return await self._generate_preop_brief(event)
        if event.type == EventType.TRANSCRIPT:
            text = event.data.get("text", "").lower()
            if any(kw in text for kw in ["scholar", "research", "literature", "evidence", "study", "paper"]):
                return await self._answer_query(event)
        return []

    async def _generate_preop_brief(self, event: AgentEvent) -> list[AgentEvent]:
        procedure = event.data.get("procedure", "Laparoscopic Cholecystectomy")
        patient = event.data.get("patient", {})

        # RAG: fetch relevant literature
        rag = RAGPipeline()
        lit_results = await rag.query(f"surgical complications {procedure}", top_k=3)
        lit_context = "\n".join(r.get("text", "") for r in lit_results) if lit_results else ""

        prompt = f"""You are The Scholar — ShalyaMitra's pre-operative intelligence.
Generate a structured surgical brief for: {procedure}

Patient: {patient.get('name', 'N/A')}, Age: {patient.get('age', 'N/A')}, 
BMI: {patient.get('bmi', 'N/A')}, ASA: {patient.get('asa', 'N/A')}
Comorbidities: {patient.get('comorbidities', 'None listed')}
Medications: {patient.get('medications', 'None listed')}
Lab results: {patient.get('labs', 'Pending')}

Relevant literature context:
{lit_context}

Return a JSON object:
{{
  "clinical_synthesis": "<2-3 sentence summary>",
  "risk_flags": [{{"severity": "warning|caution|info", "text": "<flag>"}}],
  "asa_score": <1-5>,
  "rcri_score": <0-6>,
  "key_anatomy": ["<critical structures>"],
  "recommended_positioning": "<positioning>",
  "estimated_duration_minutes": <n>,
  "critical_steps": ["<step 1>", "<step 2>"],
  "bailout_strategy": "<conversion/alternative plan>"
}}"""

        response = await self._call_llm(prompt)
        return [AgentEvent(
            type=EventType.DISPLAY_TRANSCRIPT,
            source=self.agent_id, priority=6,
            session_id=event.session_id,
            data={"speaker": "scholar", "text": response or "Pre-op brief generation in progress...",
                  "pillar": "scholar", "at": time.time()},
        )]

    async def _answer_query(self, event: AgentEvent) -> list[AgentEvent]:
        query = event.data.get("text", "")
        rag = RAGPipeline()
        results = await rag.query(query, top_k=3)
        context = "\n".join(r.get("text", "") for r in results) if results else ""

        prompt = f"""You are The Scholar. Answer this surgical query using evidence.
Query: {query}
Literature: {context}
Be precise, cite sources if available, keep under 50 words."""

        response = await self._call_llm(prompt)
        return [AgentEvent(
            type=EventType.DISPLAY_TRANSCRIPT,
            source=self.agent_id, priority=6,
            session_id=event.session_id,
            data={"speaker": "scholar", "text": response or "Searching literature...",
                  "pillar": "scholar", "at": time.time()},
        )]

    async def _call_llm(self, prompt: str) -> Optional[str]:
        if not settings.openrouter_api_key:
            return None
        try:
            http = await self._get_http()
            resp = await http.post(
                f"{settings.openrouter_base_url}/chat/completions",
                headers={"Authorization": f"Bearer {settings.openrouter_api_key}",
                         "HTTP-Referer": "https://shalyamitra.dev", "X-Title": "ShalyaMitra Scholar"},
                json={"model": settings.scholar_model, "messages": [{"role": "user", "content": prompt}],
                      "max_tokens": 500, "temperature": 0.2},
                timeout=15.0,
            )
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"].strip()
        except Exception:
            pass
        return None
