from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict

TimelineSource = Literal["simulator", "system", "human", "AI"]


class TimelineEventCreate(BaseModel):
    event: str = Field(..., min_length=1, max_length=255)
    actor: str = Field(..., min_length=1, max_length=100)
    source: TimelineSource = "system"
    description: str
    previous_value: Optional[str] = None
    new_value: Optional[str] = None
    timestamp: Optional[datetime] = None


class TimelineEventResponse(BaseModel):
    id: int
    incident_id: int
    timestamp: datetime
    event: str
    actor: str
    source: str
    description: str
    previous_value: Optional[str] = None
    new_value: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
