from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

SeverityLevel = Literal["Low", "Medium", "High", "Critical", "Not Determined"]


class AIAnalysisOutput(BaseModel):
    """
    Validated structured output format for AI suggestions.
    Guarantees strict advisory compliance and MITRE/NIST taxonomy.
    """
    incident_type: str = Field(..., description="Identified or suggested incident type")
    suggested_nist_phase: str = Field(..., description="Suggested NIST Incident Response lifecycle phase")
    suggested_severity: SeverityLevel = Field(..., description="Suggested severity level — independent from priority")
    attack_technique: str = Field(..., description="MITRE ATT&CK technique identifier e.g. T1110, T1566")
    attack_technique_name: Optional[str] = Field(None, description="Descriptive MITRE ATT&CK technique name")
    reason: str = Field(..., description="Analytical justification referencing observed telemetry and knowledge guidance")
    recommended_actions: List[str] = Field(
        default_factory=list,
        description="Prioritized actionable guidance for human incident responders",
    )
    confidence: float = Field(0.85, ge=0.0, le=1.0, description="Model confidence score between 0.0 and 1.0")
    disclaimer: str = Field(
        default="AI Suggested — Human Review Required",
        description="Mandatory advisory disclaimer stating human review is required",
    )


class AIAnalysisResponse(BaseModel):
    id: int
    incident_id: int
    incident_type: str
    suggested_nist_phase: str
    suggested_severity: str
    attack_technique: str
    attack_technique_name: Optional[str] = None
    reason: str
    recommended_actions: List[str] = []
    confidence: Optional[float] = 0.85
    disclaimer: str = "AI Suggested — Human Review Required"
    provider: str = "gemini"
    status: str = "pending"
    decision: Optional[str] = None
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    override_values: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AIReviewRequest(BaseModel):
    analysis_id: Optional[int] = None
    decision: Literal["accept", "reject", "override", "Accept", "Reject", "Override"]
    rejection_reason: Optional[str] = None
    override_values: Optional[Dict[str, Any]] = None
    apply_to_incident: bool = True
