from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.incident import Incident
from app.schemas.incident import IncidentCreate, IncidentUpdate
from app.services.clock_service import calculate_deadline
from app.services.status_service import validate_transition
from app.services.timeline_service import record_event


def create_incident(db: Session, data: IncidentCreate) -> Incident:
    """Create an incident with its server-managed clock fields."""
    detected_at = datetime.now(timezone.utc)  # Capture the detection time in UTC.
    incident = Incident(
        **data.model_dump(),
        detected_at=detected_at,
        deadline_at=calculate_deadline(detected_at),
        status="Open",
        nist_phase="Detection & Analysis",
    )
    db.add(incident)
    db.flush()  # Generate the incident identifier before recording its event.
    record_event(
        db,
        incident.id,
        "Incident Created",
        "human",
        "analyst",
        description="Incident created",
        new_value=incident.title,
    )
    db.commit()
    db.refresh(incident)
    return incident


def get_incident(db: Session, id: int) -> Incident | None:
    """Return one incident by its identifier."""
    return db.get(Incident, id)


def list_incidents(db: Session) -> list[Incident]:
    """Return incidents newest first."""
    return db.query(Incident).order_by(Incident.created_at.desc()).all()


def update_incident(
    db: Session, id: int, data: IncidentUpdate
) -> Incident | None:
    """Update only fields included in the request."""
    incident = get_incident(db, id)
    if incident is None:
        return None

    updates = data.model_dump(exclude_unset=True)
    if "status" in updates:
        new_status = updates["status"]
        if new_status != incident.status:
            validate_transition(incident.status, new_status)

    for field, value in updates.items():
        previous_value = getattr(incident, field)
        if previous_value == value:
            continue
        setattr(incident, field, value)
        if field == "status":
            record_event(
                db,
                incident.id,
                "Status Changed",
                "human",
                "analyst",
                description=f"Status changed from {previous_value} to {value}",
                previous_value=previous_value,
                new_value=value,
            )
            continue
        record_event(
            db,
            incident.id,
            "Incident Updated",
            "human",
            "analyst",
            description=f"Field {field} changed",
            previous_value=str(previous_value),
            new_value=str(value),
        )

    db.commit()
    db.refresh(incident)
    return incident
