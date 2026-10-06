from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.schemas.incident import IncidentResponse


class SimulationResponse(BaseModel):
    incident_id: int
    attack_type: str
    status: str
    detected_at: datetime
    deadline_at: datetime
    message: str
    incident: IncidentResponse


class SimulationCustomRequest(BaseModel):
    scenario_name: Optional[str] = None
    target_asset: Optional[str] = None
    target_user: Optional[str] = None
    source_ip: Optional[str] = None
