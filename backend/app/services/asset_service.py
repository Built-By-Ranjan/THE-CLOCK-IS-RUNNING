from sqlalchemy.orm import Session

from app.models.asset import Asset
from app.schemas.asset import AssetCreate, AssetUpdate
from app.services.timeline_service import record_event


def create_asset(db: Session, incident_id: int, data: AssetCreate) -> Asset:
    """Create an asset and record its timeline event."""
    asset = Asset(incident_id=incident_id, **data.model_dump())
    db.add(asset)
    record_event(
        db,
        incident_id,
        "Asset Added",
        "human",
        "analyst",
        new_value=asset.asset_name,
    )
    db.commit()
    db.refresh(asset)
    return asset


def list_assets(db: Session, incident_id: int) -> list[Asset]:
    """Return all assets for an incident."""
    return (
        db.query(Asset)
        .filter(Asset.incident_id == incident_id)
        .order_by(Asset.created_at.asc(), Asset.id.asc())
        .all()
    )


def get_asset(db: Session, incident_id: int, asset_id: int) -> Asset | None:
    """Return an asset only when it belongs to the incident."""
    return (
        db.query(Asset)
        .filter(Asset.id == asset_id, Asset.incident_id == incident_id)
        .first()
    )


def update_asset(
    db: Session, incident_id: int, asset_id: int, data: AssetUpdate
) -> Asset | None:
    """Update only sent fields and record actual changes."""
    asset = get_asset(db, incident_id, asset_id)
    if asset is None:
        return None

    previous_name = asset.asset_name
    changed = False
    for field, value in data.model_dump(exclude_unset=True).items():
        if getattr(asset, field) == value:
            continue
        setattr(asset, field, value)
        changed = True

    if changed:
        record_event(
            db,
            incident_id,
            "Asset Updated",
            "human",
            "analyst",
            previous_value=previous_name,
            new_value=asset.asset_name,
        )

    db.commit()
    db.refresh(asset)
    return asset


def delete_asset(db: Session, incident_id: int, asset_id: int) -> bool:
    """Delete an asset and record its removal."""
    asset = get_asset(db, incident_id, asset_id)
    if asset is None:
        return False

    record_event(
        db,
        incident_id,
        "Asset Removed",
        "human",
        "analyst",
        previous_value=asset.asset_name,
        new_value=asset.asset_name,
    )
    db.delete(asset)
    db.commit()
    return True
