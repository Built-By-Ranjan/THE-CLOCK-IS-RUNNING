from sqlalchemy.orm import Session

from app.models.indicator import Indicator
from app.schemas.indicator import IndicatorCreate, IndicatorUpdate
from app.services.timeline_service import record_event


def _indicator_value(indicator: Indicator) -> str:
    """Format an indicator for timeline entries."""
    return f"{indicator.type}: {indicator.value}"


def create_indicator(
    db: Session, incident_id: int, data: IndicatorCreate
) -> Indicator:
    """Create an indicator and record its timeline event."""
    indicator = Indicator(incident_id=incident_id, **data.model_dump())
    db.add(indicator)
    record_event(
        db,
        incident_id,
        "Indicator Added",
        "human",
        "analyst",
        new_value=_indicator_value(indicator),
    )
    db.commit()
    db.refresh(indicator)
    return indicator


def list_indicators(db: Session, incident_id: int) -> list[Indicator]:
    """Return all indicators for an incident."""
    return (
        db.query(Indicator)
        .filter(Indicator.incident_id == incident_id)
        .order_by(Indicator.created_at.asc(), Indicator.id.asc())
        .all()
    )


def get_indicator(
    db: Session, incident_id: int, indicator_id: int
) -> Indicator | None:
    """Return an indicator only when it belongs to the incident."""
    return (
        db.query(Indicator)
        .filter(
            Indicator.id == indicator_id,
            Indicator.incident_id == incident_id,
        )
        .first()
    )


def update_indicator(
    db: Session, incident_id: int, indicator_id: int, data: IndicatorUpdate
) -> Indicator | None:
    """Update only sent fields and record actual changes."""
    indicator = get_indicator(db, incident_id, indicator_id)
    if indicator is None:
        return None

    previous_value = _indicator_value(indicator)
    changed = False
    for field, value in data.model_dump(exclude_unset=True).items():
        if getattr(indicator, field) == value:
            continue
        setattr(indicator, field, value)
        changed = True

    if changed:
        record_event(
            db,
            incident_id,
            "Indicator Updated",
            "human",
            "analyst",
            previous_value=previous_value,
            new_value=_indicator_value(indicator),
        )

    db.commit()
    db.refresh(indicator)
    return indicator


def delete_indicator(
    db: Session, incident_id: int, indicator_id: int
) -> bool:
    """Delete an incident indicator and record its removal."""
    indicator = get_indicator(db, incident_id, indicator_id)
    if indicator is None:
        return False

    previous_value = _indicator_value(indicator)
    record_event(
        db,
        incident_id,
        "Indicator Removed",
        "human",
        "analyst",
        previous_value=previous_value,
    )
    db.delete(indicator)
    db.commit()
    return True
