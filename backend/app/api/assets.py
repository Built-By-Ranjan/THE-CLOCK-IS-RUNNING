from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.db.database import get_db
from app.schemas.asset import AssetCreate, AssetResponse, AssetUpdate
from app.services.asset_service import (
    create_asset,
    delete_asset,
    get_asset,
    list_assets,
    update_asset,
)
from app.services.incident_service import get_incident


router = APIRouter(
    prefix="/incidents/{incident_id}/assets",
    tags=["Assets"],
    dependencies=[Depends(get_current_user)],
)


def _require_incident(db: Session, incident_id: int) -> None:
    """Raise the standard error when an incident is missing."""
    if get_incident(db, incident_id) is None:
        raise HTTPException(status_code=404, detail="Incident not found")


@router.post("", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
def create_asset_endpoint(
    incident_id: int, data: AssetCreate, db: Session = Depends(get_db)
) -> AssetResponse:
    """Create and return an affected asset."""
    _require_incident(db, incident_id)
    return create_asset(db, incident_id, data)


@router.get("", response_model=list[AssetResponse])
def list_assets_endpoint(
    incident_id: int, db: Session = Depends(get_db)
) -> list[AssetResponse]:
    """Return all affected assets for an incident."""
    _require_incident(db, incident_id)
    return list_assets(db, incident_id)


@router.patch("/{asset_id}", response_model=AssetResponse)
def update_asset_endpoint(
    incident_id: int,
    asset_id: int,
    data: AssetUpdate,
    db: Session = Depends(get_db),
) -> AssetResponse:
    """Update and return an affected asset."""
    _require_incident(db, incident_id)
    asset = update_asset(db, incident_id, asset_id, data)
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asset_endpoint(
    incident_id: int, asset_id: int, db: Session = Depends(get_db)
) -> Response:
    """Delete an affected asset."""
    _require_incident(db, incident_id)
    if not delete_asset(db, incident_id, asset_id):
        raise HTTPException(status_code=404, detail="Asset not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
