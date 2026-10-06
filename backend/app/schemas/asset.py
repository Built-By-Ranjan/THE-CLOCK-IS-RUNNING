from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class AssetCreate(BaseModel):
    asset_name: str = Field(..., min_length=1, max_length=255)
    asset_type: Optional[str] = None
    description: Optional[str] = None


class AssetResponse(BaseModel):
    id: int
    incident_id: int
    asset_name: str
    asset_type: Optional[str] = None
    description: Optional[str] = None
    added_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AffectedUserCreate(BaseModel):
    username: str = Field(..., min_length=1, max_length=100)
    email: Optional[str] = None
    department: Optional[str] = None
    impact: Optional[str] = None


class AffectedUserResponse(BaseModel):
    id: int
    incident_id: int
    username: str
    email: Optional[str] = None
    department: Optional[str] = None
    impact: Optional[str] = None
    added_at: datetime

    model_config = ConfigDict(from_attributes=True)
