from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.nist_history import NISTHistory
from app.models.timeline import TimelineEvent
from app.models.incident import Incident

VALID_NIST_PHASES: List[str] = [
    "Preparation",
    "Detection & Analysis",
    "Containment, Eradication & Recovery",
    "Post-Incident Activity",
]


def validate_nist_phase(phase: str) -> None:
    """Validate that the given phase is an approved NIST IR lifecycle phase."""
    if phase not in VALID_NIST_PHASES:
        raise ValueError(f"Unknown NIST phase '{phase}'. Valid phases are: {', '.join(VALID_NIST_PHASES)}")


def record_nist_transition(
    db: Session,
    incident: Incident,
    new_phase: str,
    actor: str = "system",
    rationale: Optional[str] = None,
    source: str = "human",
) -> NISTHistory:
    """
    Record a NIST phase change for an incident, update the incident's current phase,
    and append an audit timeline event.
    """
    validate_nist_phase(new_phase)
    now = datetime.now(timezone.utc)
    old_phase = incident.current_nist_phase

    # 1. Update incident
    incident.current_nist_phase = new_phase
    incident.updated_at = now

    # 2. Record to nist_history
    history_entry = NISTHistory(
        incident_id=incident.id,
        phase=new_phase,
        timestamp=now,
        actor=actor,
        rationale=rationale,
    )
    db.add(history_entry)

    # 3. Record timeline event
    timeline_event = TimelineEvent(
        incident_id=incident.id,
        timestamp=now,
        event="NIST Phase Updated",
        actor=actor,
        source=source,
        description=f"Incident transitioned from '{old_phase}' to '{new_phase}'." + (f" Rationale: {rationale}" if rationale else ""),
        previous_value=old_phase,
        new_value=new_phase,
    )
    db.add(timeline_event)

    return history_entry
