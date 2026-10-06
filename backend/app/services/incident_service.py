from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.incident import Incident
from app.models.indicator import Indicator
from app.models.timeline import TimelineEvent
from app.models.nist_history import NISTHistory
from app.models.asset import IncidentAsset, IncidentUser
from app.models.evidence import Evidence
from app.schemas.incident import IncidentCreate, IncidentUpdate
from app.schemas.indicator import IndicatorCreate, IndicatorUpdate
from app.schemas.evidence import EvidenceCreate
from app.services.clock_service import calculate_deadline, ensure_utc
from app.services.status_service import validate_status_transition
from app.services.nist_service import record_nist_transition


def create_incident(db: Session, incident_in: IncidentCreate, actor: str = "system") -> Incident:
    """Create a new incident with UTC timestamps, 72-hour deadline, and audit logging."""
    now = datetime.now(timezone.utc)
    detected_at = ensure_utc(incident_in.detected_at or now)
    deadline_at = calculate_deadline(detected_at)

    incident = Incident(
        title=incident_in.title,
        description=incident_in.description,
        attack_type=incident_in.attack_type,
        status="Open",
        priority=incident_in.priority or "P3",
        source=incident_in.source or "human",
        current_nist_phase=incident_in.current_nist_phase or "Detection & Analysis",
        detected_at=detected_at,
        deadline_at=deadline_at,
        created_at=now,
        updated_at=now,
    )
    db.add(incident)
    db.flush()

    # Add affected assets if provided
    if incident_in.affected_assets:
        for asset_name in incident_in.affected_assets:
            db.add(
                IncidentAsset(
                    incident_id=incident.id,
                    asset_name=asset_name,
                    added_at=now,
                )
            )

    # Add affected users if provided
    if incident_in.affected_users:
        for username in incident_in.affected_users:
            db.add(
                IncidentUser(
                    incident_id=incident.id,
                    username=username,
                    added_at=now,
                )
            )

    # Initial timeline events
    db.add(
        TimelineEvent(
            incident_id=incident.id,
            timestamp=detected_at,
            event="Incident Detected",
            actor=actor,
            source=incident_in.source or "system",
            description=f"Incident '{incident.title}' detected with attack type '{incident.attack_type}'.",
        )
    )
    db.add(
        TimelineEvent(
            incident_id=incident.id,
            timestamp=now,
            event="Incident Created",
            actor=actor,
            source=incident_in.source or "human",
            description="Incident record formally created in repository.",
        )
    )

    # Initial NIST History
    db.add(
        NISTHistory(
            incident_id=incident.id,
            phase=incident.current_nist_phase,
            timestamp=now,
            actor=actor,
            rationale="Initial incident creation and categorization.",
        )
    )

    db.commit()
    db.refresh(incident)
    return incident


def get_incident_by_id(db: Session, incident_id: int) -> Optional[Incident]:
    """Retrieve an incident by ID with all relationships eagerly loaded."""
    return db.query(Incident).filter(Incident.id == incident_id).first()


def list_incidents(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    attack_type: Optional[str] = None,
    status_filter: Optional[str] = None,
) -> Tuple[List[Incident], int]:
    """List incidents with filtering and pagination."""
    query = db.query(Incident)
    if attack_type:
        query = query.filter(Incident.attack_type.ilike(f"%{attack_type}%"))
    if status_filter:
        query = query.filter(Incident.status == status_filter)

    total = query.count()
    items = query.order_by(Incident.created_at.desc()).offset(skip).limit(limit).all()
    return items, total


def update_incident(
    db: Session,
    incident: Incident,
    incident_in: IncidentUpdate,
    actor: str = "human",
) -> Incident:
    """Update incident fields and record state changes in the audit timeline."""
    now = datetime.now(timezone.utc)
    changed = False

    # 1. Status transition check
    if incident_in.status is not None and incident_in.status != incident.status:
        try:
            validate_status_transition(incident.status, incident_in.status)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

        old_status = incident.status
        incident.status = incident_in.status
        changed = True

        db.add(
            TimelineEvent(
                incident_id=incident.id,
                timestamp=now,
                event="Status Changed",
                actor=actor,
                source="human",
                description=f"Status changed from '{old_status}' to '{incident.status}'."
                + (f" Rationale: {incident_in.rationale}" if incident_in.rationale else ""),
                previous_value=old_status,
                new_value=incident.status,
            )
        )

    # 2. Priority change check
    if incident_in.priority is not None and incident_in.priority != incident.priority:
        old_priority = incident.priority
        incident.priority = incident_in.priority
        changed = True

        db.add(
            TimelineEvent(
                incident_id=incident.id,
                timestamp=now,
                event="Priority Changed",
                actor=actor,
                source="human",
                description=f"Priority updated from '{old_priority}' to '{incident.priority}'.",
                previous_value=old_priority,
                new_value=incident.priority,
            )
        )

    # 3. NIST phase transition check
    if incident_in.current_nist_phase is not None and incident_in.current_nist_phase != incident.current_nist_phase:
        record_nist_transition(
            db=db,
            incident=incident,
            new_phase=incident_in.current_nist_phase,
            actor=actor,
            rationale=incident_in.rationale,
            source="human",
        )
        changed = True

    # 4. Other fields
    if incident_in.title is not None and incident_in.title != incident.title:
        incident.title = incident_in.title
        changed = True

    if incident_in.description is not None and incident_in.description != incident.description:
        incident.description = incident_in.description
        changed = True

    if incident_in.attack_type is not None and incident_in.attack_type != incident.attack_type:
        incident.attack_type = incident_in.attack_type
        changed = True

    if changed:
        incident.updated_at = now
        db.commit()
        db.refresh(incident)

    return incident


def delete_incident(db: Session, incident_id: int) -> bool:
    """Delete an incident and cascades all dependent records."""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        return False
    db.delete(incident)
    db.commit()
    return True


def add_indicator(
    db: Session,
    incident_id: int,
    indicator_in: IndicatorCreate,
    actor: str = "human",
) -> Indicator:
    """Add an indicator to an incident and log a timeline event."""
    incident = get_incident_by_id(db, incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")

    now = datetime.now(timezone.utc)
    indicator = Indicator(
        incident_id=incident_id,
        type=indicator_in.type,
        value=indicator_in.value,
        description=indicator_in.description,
        source=indicator_in.source or "system",
        created_at=now,
        updated_at=now,
    )
    db.add(indicator)
    db.flush()

    db.add(
        TimelineEvent(
            incident_id=incident_id,
            timestamp=now,
            event="Indicator Added",
            actor=actor,
            source="human",
            description=f"Added indicator [{indicator.type}]: {indicator.value}",
            new_value=f"{indicator.type}: {indicator.value}",
        )
    )
    db.commit()
    db.refresh(indicator)
    return indicator


def update_indicator(
    db: Session,
    incident_id: int,
    indicator_id: int,
    indicator_in: IndicatorUpdate,
    actor: str = "human",
) -> Indicator:
    """Update an indicator and log a timeline event."""
    indicator = db.query(Indicator).filter(
        Indicator.id == indicator_id,
        Indicator.incident_id == incident_id,
    ).first()
    if not indicator:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Indicator not found")

    now = datetime.now(timezone.utc)
    old_value = f"{indicator.type}: {indicator.value}"

    if indicator_in.type is not None:
        indicator.type = indicator_in.type
    if indicator_in.value is not None:
        indicator.value = indicator_in.value
    if indicator_in.description is not None:
        indicator.description = indicator_in.description

    indicator.updated_at = now
    new_value = f"{indicator.type}: {indicator.value}"

    db.add(
        TimelineEvent(
            incident_id=incident_id,
            timestamp=now,
            event="Indicator Updated",
            actor=actor,
            source="human",
            description=f"Updated indicator from '{old_value}' to '{new_value}'.",
            previous_value=old_value,
            new_value=new_value,
        )
    )
    db.commit()
    db.refresh(indicator)
    return indicator


def delete_indicator(
    db: Session,
    incident_id: int,
    indicator_id: int,
    actor: str = "human",
) -> bool:
    """Delete an indicator and log a timeline event."""
    indicator = db.query(Indicator).filter(
        Indicator.id == indicator_id,
        Indicator.incident_id == incident_id,
    ).first()
    if not indicator:
        return False

    now = datetime.now(timezone.utc)
    desc = f"Removed indicator [{indicator.type}]: {indicator.value}"
    old_val = f"{indicator.type}: {indicator.value}"

    db.delete(indicator)
    db.add(
        TimelineEvent(
            incident_id=incident_id,
            timestamp=now,
            event="Indicator Removed",
            actor=actor,
            source="human",
            description=desc,
            previous_value=old_val,
        )
    )
    db.commit()
    return True


def add_evidence(
    db: Session,
    incident_id: int,
    evidence_in: EvidenceCreate,
    actor: str = "human",
) -> Evidence:
    """Add evidence item to an incident and log a timeline event."""
    incident = get_incident_by_id(db, incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")

    now = datetime.now(timezone.utc)
    collected_at = ensure_utc(evidence_in.collected_at or now)

    evidence = Evidence(
        incident_id=incident_id,
        type=evidence_in.type,
        name=evidence_in.name,
        source=evidence_in.source,
        collected_at=collected_at,
        collector=evidence_in.collector,
        sha256=evidence_in.sha256,
        status=evidence_in.status or "collected",
        details=evidence_in.details,
        created_at=now,
    )
    db.add(evidence)
    db.flush()

    db.add(
        TimelineEvent(
            incident_id=incident_id,
            timestamp=now,
            event="Evidence Logged",
            actor=actor,
            source="human",
            description=f"Evidence recorded: '{evidence.name}' ({evidence.type}) from {evidence.source}. SHA-256: {evidence.sha256 or 'N/A'}",
            new_value=evidence.name,
        )
    )
    db.commit()
    db.refresh(evidence)
    return evidence
