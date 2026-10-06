from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, ConfigDict

from app.schemas.indicator import IndicatorResponse
from app.schemas.timeline import TimelineEventResponse
from app.schemas.nist import NISTHistoryResponse, NISTPhase
from app.schemas.asset import AssetResponse, AffectedUserResponse
from app.schemas.evidence import EvidenceResponse

IncidentStatus = Literal[
    "Open",
    "Under Investigation",
    "Contained",
    "Eradicated",
    "Recovered",
    "Closed",
]

IncidentPriority = Literal["P1", "P2", "P3", "P4"]


class IncidentCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    attack_type: str = Field(..., min_length=1, max_length=100)
    priority: IncidentPriority = "P3"
    source: str = "human"
    current_nist_phase: NISTPhase = "Detection & Analysis"
    detected_at: Optional[datetime] = None
    affected_assets: Optional[List[str]] = []
    affected_users: Optional[List[str]] = []


class IncidentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    attack_type: Optional[str] = Field(None, min_length=1, max_length=100)
    status: Optional[IncidentStatus] = None
    priority: Optional[IncidentPriority] = None
    current_nist_phase: Optional[NISTPhase] = None
    rationale: Optional[str] = None


class IncidentResponse(BaseModel):
    id: int
    title: str
    description: str
    attack_type: str
    status: str
    priority: str
    source: str
    current_nist_phase: str
    detected_at: datetime
    deadline_at: datetime
    created_at: datetime
    updated_at: datetime

    indicators: List[IndicatorResponse] = []
    timeline_events: List[TimelineEventResponse] = []
    nist_history: List[NISTHistoryResponse] = []
    affected_assets: List[AssetResponse] = []
    affected_users: List[AffectedUserResponse] = []
    evidence: List[EvidenceResponse] = []

    model_config = ConfigDict(from_attributes=True)


class IncidentListResponse(BaseModel):
    items: List[IncidentResponse]
    total: int
