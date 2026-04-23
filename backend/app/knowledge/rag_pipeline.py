"""
ShalyaMitra — RAG Pipeline

Retrieval-Augmented Generation pipeline for the Oracle and Scholar agents.

Architecture:
  1. Query text → NV-Embed-v2 embedding
  2. Qdrant vector search (top-k nearest chunks)
  3. Cross-encoder reranking
  4. Context assembly → LLM prompt

Collections:
  - shalyatantra: Sushruta Samhita, Ashtanga Hridayam, Marma texts
  - medical_kb:   Modern surgical/anaesthetic knowledge base
  - drug_db:      Pharmacological reference (drug interactions, doses)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from app.config import settings


@dataclass
class RAGResult:
    """A single retrieved chunk with metadata."""
    text: str
    source: str             # e.g. "Sushruta Samhita, Sharira 6.16"
    collection: str         # Which Qdrant collection
    score: float            # Similarity score
    metadata: dict[str, Any]


@dataclass
class RAGResponse:
    """Complete RAG response with context for LLM."""
    query: str
    results: list[RAGResult]
    context_text: str       # Assembled context for LLM prompt
    total_chunks: int


class RAGPipeline:
    """
    Main RAG pipeline.

    Phase 1: Returns mock results for demo/testing.
    Phase 2: Connects to Qdrant + NV-Embed-v2 via NIM.
    """

    def __init__(self):
        self._qdrant_client = None
        self._embed_model = None

    async def initialize(self):
        """Initialize Qdrant client and embedding model."""
        # TODO: Phase 2 — connect to Qdrant and NIM embedding endpoint
        # from qdrant_client import AsyncQdrantClient
        # self._qdrant_client = AsyncQdrantClient(url=settings.qdrant_url)
        pass

    async def query(
        self,
        query: str,
        collections: list[str] | None = None,
        top_k: int = 5,
    ) -> RAGResponse:
        """
        Run a RAG query against the knowledge base.

        Args:
            query: Natural language query
            collections: Which collections to search (default: all)
            top_k: Number of results per collection
        """
        if collections is None:
            collections = [
                settings.qdrant_collection_shalyatantra,
                settings.qdrant_collection_medical,
            ]

        # Phase 1: Mock results
        results = self._mock_query(query, collections, top_k)

        # Assemble context
        context_parts = []
        for r in results:
            context_parts.append(f"[{r.source}]\n{r.text}")

        return RAGResponse(
            query=query,
            results=results,
            context_text="\n\n---\n\n".join(context_parts),
            total_chunks=len(results),
        )

    async def query_marma(self, procedure: str, anatomy_region: str) -> RAGResponse:
        """
        Specialized Marma query for the Oracle agent.

        Searches the Shalyatantra corpus for Marma points relevant
        to the given procedure and anatomical region.
        """
        query = f"Marma points near {anatomy_region} relevant to {procedure}"
        return await self.query(query, collections=[settings.qdrant_collection_shalyatantra], top_k=3)

    async def query_drug(self, drug_name: str) -> RAGResponse:
        """
        Drug information query for the Pharmacist agent.
        """
        query = f"Drug profile: {drug_name} — dosing, interactions, contraindications"
        return await self.query(query, collections=[settings.qdrant_collection_drugs], top_k=3)

    def _mock_query(self, query: str, collections: list[str], top_k: int) -> list[RAGResult]:
        """Return mock results for demo mode."""
        mock_results = []

        if "marma" in query.lower() or "nabhi" in query.lower():
            mock_results.append(RAGResult(
                text=(
                    "मर्माणि नाम ते विशेषायतनानि धातूनां, तेषु स्वभावत एव विशेषेण प्राणास्तिष्ठन्ति। "
                    "Marmas are vital junction points where life force (Prana) resides. "
                    "Nābhi Marma is classified as Sadya Praṇahara — injury causes immediate death."
                ),
                source="Suśruta Saṃhitā, Śārīrasthāna 6.16",
                collection="shalyatantra",
                score=0.94,
                metadata={"chapter": "Sharira 6", "shloka": "16", "classification": "Sadya Pranahara"},
            ))

        if "cholecystectomy" in query.lower() or "gallbladder" in query.lower():
            mock_results.append(RAGResult(
                text=(
                    "Critical View of Safety (CVS) is the gold standard for identifying "
                    "the cystic duct and cystic artery during laparoscopic cholecystectomy. "
                    "Two structures and only two should be seen entering the gallbladder."
                ),
                source="Strasberg SM et al., J Am Coll Surg 2010",
                collection="medical_kb",
                score=0.91,
                metadata={"doi": "10.1016/j.jamcollsurg.2010.02.053"},
            ))

        if "fentanyl" in query.lower() or "drug" in query.lower():
            mock_results.append(RAGResult(
                text=(
                    "Fentanyl: Synthetic opioid, 100x morphine potency. "
                    "IV onset 1-2 min, duration 30-60 min. "
                    "Interaction with Amlodipine: Minor additive hypotension."
                ),
                source="Stoelting's Pharmacology, 6th Ed",
                collection="drug_db",
                score=0.89,
                metadata={"drug_class": "opioid", "route": "IV"},
            ))

        return mock_results[:top_k]


# Singleton
_pipeline: Optional[RAGPipeline] = None


def get_rag_pipeline() -> RAGPipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = RAGPipeline()
    return _pipeline
