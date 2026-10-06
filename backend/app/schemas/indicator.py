from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict

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


class IndicatorCreate(BaseModel):
    type: IndicatorType
    value: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    source: str = "system"


class IndicatorUpdate(BaseModel):
    type: Optional[IndicatorType] = None
    value: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None


class IndicatorResponse(BaseModel):
    id: int
    incident_id: int
    type: str
    value: str
    description: Optional[str]
    source: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
