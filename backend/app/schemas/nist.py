from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict

NISTPhase = Literal[
    "Preparation",
    "Detection & Analysis",
    "Containment, Eradication & Recovery",
    "Post-Incident Activity",
]


class NISTPhaseUpdate(BaseModel):
    phase: NISTPhase
    rationale: Optional[str] = None


class NISTHistoryResponse(BaseModel):
    id: int
    incident_id: int
    phase: str
    timestamp: datetime
    actor: str
    rationale: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
