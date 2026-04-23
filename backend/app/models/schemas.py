"""
Pydantic schemas shared by REST, WebSocket, and GPU helpers.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# --- WebSocket / Theatre wire (documented event shapes) --------------------

EvTranscript = dict[str, Any]
EvAlert = dict[str, Any]
EvVitals = dict[str, Any]
EvPhase = dict[str, Any]
EvPong = dict[str, Any]
EvError = dict[str, Any]


class AriaMode(str, Enum):
    """Theatre ARIA gating: how chatty Nael and alerts are."""

    silent = "silent"
    reactive = "reactive"


# --- Session CRUD -----------------------------------------------------------


class SessionStatus(str, Enum):
    scheduled = "scheduled"
    active = "active"
    completed = "completed"
    cancelled = "cancelled"


class SessionCreate(BaseModel):
    model_config = ConfigDict(extra="allow")

    procedure_name: str = ""
    patient_name: str = ""
    patient_age: int = 0
    patient_weight_kg: float = 70.0
    patient_bmi: float = 25.0
    asa_grade: int = 2
    comorbidities: str = ""


class SessionUpdate(BaseModel):
    model_config = ConfigDict(extra="allow")

    status: Optional[SessionStatus] = None
    current_mode: Optional[str] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None


class SessionRead(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
    created_by: str
    status: str
    current_mode: Optional[str] = None
    procedure_name: Optional[str] = None
    patient_name: Optional[str] = None
    patient_age: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


# --- Pre-op / Post-op -------------------------------------------------------


class PreOpRequest(BaseModel):
    session_id: str


class PreOpAnalysis(BaseModel):
    session_id: str
    clinical_synthesis: str
    risk_flags: list[dict[str, Any]]
    drug_interactions: list[dict[str, Any]]
    asa_score: int
    rcri_score: int
    anatomical_deviations: list[str]
    ayurvedic_assessment: dict[str, Any]
    marma_zones: list[dict[str, Any]]


class PostOpReportRequest(BaseModel):
    session_id: str


class PostOpReport(BaseModel):
    session_id: str
    operative_timeline: list[dict[str, Any]]
    anaesthetic_record: dict[str, Any]
    intraoperative_findings: str
    deviations: list[str]
    ai_intervention_log: list[dict[str, Any]]
    handover_brief: str
    recommendations: list[str]


# --- Profiles -------------------------------------------------------------


class ProfileBase(BaseModel):
    model_config = ConfigDict(extra="allow")

    full_name: Optional[str] = None
    title: Optional[str] = None
    hospital: Optional[str] = None
    avatar_url: Optional[str] = None


# --- GPU orchestrator -------------------------------------------------------


class GpuInstanceState(str, Enum):
    provisioning = "provisioning"
    ready = "ready"
    terminating = "terminating"
    terminated = "terminated"


class GpuSessionRequest(BaseModel):
    session_id: UUID
    provider: str = Field(default="demo")


class GpuSessionStatus(BaseModel):
    model_config = ConfigDict(extra="allow")

    session_id: UUID
    provider: str
    status: GpuInstanceState
    started_at: datetime
    endpoint_url: Optional[str] = None
    livekit_url: Optional[str] = None
    estimated_cost_inr: Optional[float] = None
