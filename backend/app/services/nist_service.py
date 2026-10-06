from sqlalchemy.orm import Session

from app.models.incident import Incident
from app.models.nist_history import NistHistory
from app.services.timeline_service import record_event


ALLOWED_NIST_PHASES = (
    "Preparation",
    "Detection & Analysis",
    "Containment, Eradication & Recovery",
    "Post-Incident Activity",
)


class InvalidNistPhase(ValueError):
    """Raised when an incident is assigned an unsupported NIST phase."""


def change_nist_phase(
    db: Session,
    incident: Incident,
    new_phase: str,
    reason: str | None,
    actor: str = "analyst",
) -> Incident:
    """Change an incident's NIST phase and record both histories atomically."""
    if new_phase not in ALLOWED_NIST_PHASES:
        valid_phases = ", ".join(ALLOWED_NIST_PHASES)
        raise InvalidNistPhase(
            f"Invalid NIST phase '{new_phase}'. Valid phases: {valid_phases}"
        )
    if new_phase == incident.nist_phase:
        return incident

    previous_phase = incident.nist_phase
    try:
        history = NistHistory(
            incident_id=incident.id,
            previous_phase=previous_phase,
            new_phase=new_phase,
            actor=actor,
            reason=reason,
        )
        db.add(history)
        incident.nist_phase = new_phase
        record_event(
            db,
            incident.id,
            "NIST Phase Changed",
            "human",
            actor,
            previous_value=previous_phase,
            new_value=new_phase,
            description=f"NIST phase changed from {previous_phase} to {new_phase}",
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(incident)
    return incident


def list_nist_history(db: Session, incident_id: int) -> list[NistHistory]:
    """Return NIST phase history newest first."""
    return (
        db.query(NistHistory)
        .filter(NistHistory.incident_id == incident_id)
        .order_by(NistHistory.timestamp.desc(), NistHistory.id.desc())
        .all()
    )
