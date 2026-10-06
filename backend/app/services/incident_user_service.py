from sqlalchemy.orm import Session

from app.models.incident_user import IncidentUser
from app.schemas.incident_user import IncidentUserCreate, IncidentUserUpdate
from app.services.timeline_service import record_event


def create_incident_user(
    db: Session, incident_id: int, data: IncidentUserCreate
) -> IncidentUser:
    """Create an affected user and record its timeline event."""
    user = IncidentUser(incident_id=incident_id, **data.model_dump())
    db.add(user)
    record_event(
        db,
        incident_id,
        "Affected User Added",
        "human",
        "analyst",
        new_value=user.user_name,
    )
    db.commit()
    db.refresh(user)
    return user


def list_incident_users(db: Session, incident_id: int) -> list[IncidentUser]:
    """Return all affected users for an incident."""
    return (
        db.query(IncidentUser)
        .filter(IncidentUser.incident_id == incident_id)
        .order_by(IncidentUser.created_at.asc(), IncidentUser.id.asc())
        .all()
    )


def get_incident_user(
    db: Session, incident_id: int, user_id: int
) -> IncidentUser | None:
    """Return a user only when it belongs to the incident."""
    return (
        db.query(IncidentUser)
        .filter(
            IncidentUser.id == user_id,
            IncidentUser.incident_id == incident_id,
        )
        .first()
    )


def update_incident_user(
    db: Session, incident_id: int, user_id: int, data: IncidentUserUpdate
) -> IncidentUser | None:
    """Update only sent fields and record actual changes."""
    user = get_incident_user(db, incident_id, user_id)
    if user is None:
        return None

    previous_name = user.user_name
    changed = False
    for field, value in data.model_dump(exclude_unset=True).items():
        if getattr(user, field) == value:
            continue
        setattr(user, field, value)
        changed = True

    if changed:
        record_event(
            db,
            incident_id,
            "Affected User Updated",
            "human",
            "analyst",
            previous_value=previous_name,
            new_value=user.user_name,
        )

    db.commit()
    db.refresh(user)
    return user


def delete_incident_user(db: Session, incident_id: int, user_id: int) -> bool:
    """Delete an affected user and record its removal."""
    user = get_incident_user(db, incident_id, user_id)
    if user is None:
        return False

    record_event(
        db,
        incident_id,
        "Affected User Removed",
        "human",
        "analyst",
        previous_value=user.user_name,
        new_value=user.user_name,
    )
    db.delete(user)
    db.commit()
    return True
