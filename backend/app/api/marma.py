"""
ShalyaMitra — Marma Knowledge API

REST endpoints for querying the 107 Marma database:
  - Full database listing with pagination
  - Lookup by procedure (surgical relevance)
  - Lookup by body region
  - Lookup by classification (severity)
  - Individual Marma detail
  - Database statistics
"""

from __future__ import annotations
from typing import Optional
from fastapi import APIRouter, Query

from app.knowledge.marma_db import (
    MARMA_DB, CLASSIFICATION_INFO, TISSUE_TYPES,
    get_marma_stats, get_marma_for_procedure, get_marma_by_id,
    get_marma_by_zone, get_marma_by_classification, get_marma_by_region,
    get_critical_marmas,
)

router = APIRouter()


@router.get("/stats")
async def marma_stats():
    """Get Marma database statistics — counts by classification and region."""
    return get_marma_stats()


@router.get("/all")
async def list_all_marmas(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=107),
):
    """List all 107 Marma points with pagination."""
    subset = MARMA_DB[offset : offset + limit]
    return {
        "total": len(MARMA_DB),
        "offset": offset,
        "limit": limit,
        "marmas": subset,
    }


@router.get("/procedure/{procedure_name}")
async def marmas_for_procedure(procedure_name: str):
    """Get Marma points relevant to a specific surgical procedure."""
    results = get_marma_for_procedure(procedure_name)
    return {
        "procedure": procedure_name,
        "count": len(results),
        "marmas": results,
    }


@router.get("/region/{region}")
async def marmas_by_region(region: str):
    """Get Marma points by body region (e.g. 'head', 'neck', 'abdomen')."""
    results = get_marma_by_region(region)
    return {
        "region": region,
        "count": len(results),
        "marmas": results,
    }


@router.get("/classification/{classification}")
async def marmas_by_classification(classification: str):
    """Get Marma points by Sushruta classification severity."""
    results = get_marma_by_classification(classification)
    info = CLASSIFICATION_INFO.get(classification, {})
    return {
        "classification": classification,
        "info": info,
        "count": len(results),
        "marmas": results,
    }


@router.get("/zone/{zone}")
async def marmas_by_zone(zone: str):
    """Get Marma points near an anatomical zone or structure."""
    results = get_marma_by_zone(zone)
    return {
        "zone": zone,
        "count": len(results),
        "marmas": results,
    }


@router.get("/critical")
async def critical_marmas():
    """Get all Sadya Pranahara (immediately fatal) Marma points."""
    results = get_critical_marmas()
    return {
        "classification": "Sadya Pranahara",
        "meaning": "Immediately fatal if injured",
        "count": len(results),
        "marmas": results,
    }


@router.get("/classifications")
async def classification_reference():
    """Get the 5 Sushruta Marma classification categories with shlokas."""
    return {
        "classifications": CLASSIFICATION_INFO,
        "tissue_types": TISSUE_TYPES,
    }


@router.get("/{marma_id}")
async def get_marma(marma_id: str):
    """Get a specific Marma point by ID."""
    marma = get_marma_by_id(marma_id)
    if not marma:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Marma '{marma_id}' not found")
    return marma
