from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, model_validator

from app.services.clock_service import get_clock_status
from app.services.status_service import Status


class IncidentCreate(BaseModel):  # Define fields accepted when creating an incident.
    model_config = ConfigDict(extra="forbid")

    title: str
    description: str | None = None
    what_happened: str | None = None
    source: str | None = None
    initial_impact: str | None = None
    attack_type: str | None = None
    severity: str = "Not Determined"


class IncidentUpdate(BaseModel):  # Define optional fields accepted for updates.
    model_config = ConfigDict(extra="forbid")

    title: str | None = None
    description: str | None = None
    what_happened: str | None = None
    source: str | None = None
    initial_impact: str | None = None
    attack_type: str | None = None
    severity: str | None = None
    status: Status | None = None
    notes: str | None = None


class IncidentResponse(BaseModel):  # Define the incident response payload.
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None = None
    what_happened: str | None = None
    source: str | None = None
    initial_impact: str | None = None
    attack_type: str | None = None
    severity: str | None = None
    nist_phase: str | None = None
    status: str | None = None
    notes: str | None = None
    detected_at: datetime | None = None
    deadline_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    clock: dict[str, datetime | str]

    @model_validator(mode="before")
    @classmethod
    def add_clock(cls, value: Any) -> Any:  # Add clock status while reading an ORM object.
        if isinstance(value, dict):
            data = value.copy()
        else:
            data = {
                field: getattr(value, field)
                for field in cls.model_fields
                if field != "clock" and hasattr(value, field)
            }

        data["clock"] = get_clock_status(data["detected_at"], data["deadline_at"])
        return data
