from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AssetCreate(BaseModel):  # Define fields accepted when adding an asset.
    asset_name: str
    asset_type: str | None = None


class AssetUpdate(BaseModel):  # Define optional asset update fields.
    asset_name: str | None = None
    asset_type: str | None = None


class AssetResponse(BaseModel):  # Define the affected asset response payload.
    model_config = ConfigDict(from_attributes=True)

    id: int
    incident_id: int
    asset_name: str
    asset_type: str | None = None
    created_at: datetime | None = None
