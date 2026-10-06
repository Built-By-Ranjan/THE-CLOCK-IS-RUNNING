from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator


IndicatorType = Literal[
    "IP",
    "Domain",
    "URL",
    "Email",
    "File Hash",
    "Username",
    "Process",
    "Command",
    "Other",
]

ALLOWED_INDICATOR_TYPES = (
    "IP",
    "Domain",
    "URL",
    "Email",
    "File Hash",
    "Username",
    "Process",
    "Command",
    "Other",
)


class IndicatorCreate(BaseModel):  # Define fields accepted when adding an indicator.
    type: IndicatorType
    value: str
    note: str | None = None

    @field_validator("type", mode="before")
    @classmethod
    def validate_type(cls, value: object) -> object:
        if value not in ALLOWED_INDICATOR_TYPES:
            valid_types = ", ".join(ALLOWED_INDICATOR_TYPES)
            raise ValueError(f"must be one of: {valid_types}")
        return value


class IndicatorUpdate(BaseModel):  # Define optional indicator update fields.
    type: IndicatorType | None = None
    value: str | None = None
    note: str | None = None

    @field_validator("type", mode="before")
    @classmethod
    def validate_type(cls, value: object) -> object:
        if value is None:
            return value
        if value not in ALLOWED_INDICATOR_TYPES:
            valid_types = ", ".join(ALLOWED_INDICATOR_TYPES)
            raise ValueError(f"must be one of: {valid_types}")
        return value


class IndicatorResponse(BaseModel):  # Define the indicator response payload.
    model_config = ConfigDict(from_attributes=True)

    id: int
    incident_id: int
    type: str | None = None
    value: str | None = None
    note: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
