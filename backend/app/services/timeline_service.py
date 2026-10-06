from sqlalchemy.orm import Session

from app.models.timeline import TimelineEvent


ALLOWED_SOURCE_TYPES = {"human", "AI", "system", "simulator"}


def record_event(
    db,
    incident_id,
    event_type,
    source_type,
    actor,
    description=None,
    previous_value=None,
    new_value=None,
):
    """Add a timeline event without committing the session."""
    if source_type not in ALLOWED_SOURCE_TYPES:
        raise ValueError(f"Invalid source_type: {source_type}")

    event = TimelineEvent(
        incident_id=incident_id,
        event_type=event_type,
        source_type=source_type,
        actor=actor,
        description=description,
        previous_value=previous_value,
        new_value=new_value,
    )
    db.add(event)
    return event


def get_timeline(db: Session, incident_id: int) -> list[TimelineEvent]:
    """Return an incident timeline from oldest to newest."""
    return (
        db.query(TimelineEvent)
        .filter(TimelineEvent.incident_id == incident_id)
        .order_by(TimelineEvent.timestamp.asc(), TimelineEvent.id.asc())
        .all()
    )
