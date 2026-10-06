from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TimelineEventResponse(BaseModel):  # Define the timeline event response.
    model_config = ConfigDict(from_attributes=True)

    id: int
    incident_id: int
    timestamp: datetime
    event_type: str
    actor: str | None = None
    source_type: str
    previous_value: str | None = None
    new_value: str | None = None
    description: str | None = None
