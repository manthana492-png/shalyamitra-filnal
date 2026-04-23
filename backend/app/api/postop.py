"""
ShalyaMitra — Post-Operative Report API (The Chronicler)

Generates the Intraoperative Chronicle and Handover Brief
after surgery completion. The frontend's PostOp page calls this.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.auth.jwt import get_current_user, AuthUser
from app.models.schemas import PostOpReportRequest, PostOpReport

router = APIRouter()


@router.post("/generate", response_model=PostOpReport)
async def generate_report(
    body: PostOpReportRequest,
    user: AuthUser = Depends(get_current_user),
):
    """
    Generate post-operative report.

    Phase 1: Returns mock structured report.
    Phase 2: Chronicler agent aggregates all session data and calls
             OpenRouter for narrative generation.
    """
    # TODO: Wire to Chronicler agent
    # 1. Fetch all transcripts, alerts, vitals for this session
    # 2. Build operative timeline from event log
    # 3. Call OpenRouter (Claude) for narrative generation
    # 4. Generate handover brief
    # 5. Store in MinIO + PostgreSQL
    return PostOpReport(
        session_id=body.session_id,
        operative_timeline=[
            {"at": 0, "event": "Session started", "phase": "preparation"},
            {"at": 30, "event": "Access phase — insufflation", "phase": "access"},
            {"at": 60, "event": "Dissection began", "phase": "dissection"},
            {"at": 210, "event": "Haemorrhage alert — resolved", "phase": "dissection"},
            {"at": 300, "event": "Closure — instrument count confirmed", "phase": "closure"},
        ],
        anaesthetic_record={
            "induction": "Propofol 130mg IV, Fentanyl 100μg IV, Rocuronium 40mg IV",
            "maintenance": "Sevoflurane MAC 1.0, Remifentanil 0.15μg/kg/min",
            "total_opioid": "Fentanyl 100μg",
            "fluids": "Ringer's Lactate 1000mL",
        },
        intraoperative_findings=(
            "Gallbladder moderately distended with multiple calculi. "
            "Calot's triangle dissected — Critical View of Safety achieved. "
            "Small cystic artery branch encountered and cauterised."
        ),
        deviations=["Small arterial bleeding episode at T+3:30 — resolved with cautery"],
        ai_intervention_log=[
            {"at": 85, "pillar": "nael", "type": "CVS check warning"},
            {"at": 92, "pillar": "monitor", "type": "HR trend notification"},
            {"at": 122, "pillar": "oracle", "type": "Marma proximity advisory"},
            {"at": 210, "pillar": "haemorrhage", "type": "CRITICAL — arterial bleed detected"},
            {"at": 248, "pillar": "advocate", "type": "Platelet function cross-check"},
        ],
        handover_brief=(
            "Uneventful laparoscopic cholecystectomy. One arterial bleeding episode "
            "at T+3:30 — controlled with cautery. Instrument count complete. "
            "Monitor for signs of bleeding given borderline platelet count. "
            "Resume Amlodipine. DVT prophylaxis as planned."
        ),
        recommendations=[
            "Monitor drain output (if placed) for 4 hours",
            "Recheck platelet count at 6 hours post-op",
            "Resume oral Amlodipine 5mg once tolerating orals",
            "LMWH DVT prophylaxis at 6 hours post-op",
            "Oral liquids at 4 hours, diet as tolerated",
        ],
    )


@router.get("/{session_id}", response_model=PostOpReport)
async def get_report(
    session_id: str,
    user: AuthUser = Depends(get_current_user),
):
    """Retrieve a previously generated post-op report."""
    # TODO: Fetch from database/MinIO
    raise HTTPException(status_code=404, detail="Report not found — generate first")
