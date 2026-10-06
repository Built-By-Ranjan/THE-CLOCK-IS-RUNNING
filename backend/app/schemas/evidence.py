from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class EvidenceCreate(BaseModel):
    type: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=255)
    source: str = Field(..., min_length=1, max_length=100)
    collector: str = Field(..., min_length=1, max_length=100)
    sha256: Optional[str] = Field(None, max_length=64)
    status: str = "collected"
    details: Optional[str] = None
    collected_at: Optional[datetime] = None


class EvidenceResponse(BaseModel):
    id: int
    incident_id: int
    type: str
    name: str
    source: str
    collected_at: datetime
    collector: str
    sha256: Optional[str] = None
    status: str
    details: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
