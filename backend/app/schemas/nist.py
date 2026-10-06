from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NistPhaseChange(BaseModel):  # Define the dedicated phase-change request.
    new_phase: str
    reason: str | None = None


class NistHistoryResponse(BaseModel):  # Define the NIST phase history response.
    model_config = ConfigDict(from_attributes=True)

    id: int
    incident_id: int
    previous_phase: str
    new_phase: str
    actor: str
    reason: str | None = None
    timestamp: datetime
