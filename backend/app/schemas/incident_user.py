from datetime import datetime

from pydantic import BaseModel, ConfigDict


class IncidentUserCreate(BaseModel):  # Define fields accepted when adding a user.
    user_name: str
    user_identifier: str | None = None


class IncidentUserUpdate(BaseModel):  # Define optional affected-user update fields.
    user_name: str | None = None
    user_identifier: str | None = None


class IncidentUserResponse(BaseModel):  # Define the affected user response payload.
    model_config = ConfigDict(from_attributes=True)

    id: int
    incident_id: int
    user_name: str
    user_identifier: str | None = None
    created_at: datetime | None = None
