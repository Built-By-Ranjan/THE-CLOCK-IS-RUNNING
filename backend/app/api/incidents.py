from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.api.deps import get_optional_current_user
from app.models.user import User
from app.models.incident import Incident
from app.models.indicator import Indicator
from app.models.timeline import TimelineEvent
from app.models.nist_history import NISTHistory
from app.models.asset import IncidentAsset, IncidentUser
from app.models.evidence import Evidence
from app.schemas.incident import (
    IncidentCreate,
    IncidentUpdate,
    IncidentResponse,
    IncidentListResponse,
)
from app.schemas.indicator import (
    IndicatorCreate,
    IndicatorUpdate,
    IndicatorResponse,
)
from app.schemas.timeline import TimelineEventResponse
from app.schemas.nist import NISTHistoryResponse, NISTPhaseUpdate
from app.schemas.evidence import EvidenceCreate, EvidenceResponse
from app.schemas.asset import AssetCreate, AssetResponse, AffectedUserCreate, AffectedUserResponse
from app.services.incident_service import (
    create_incident,
    get_incident_by_id,
    list_incidents,
    update_incident,
    delete_incident,
    add_indicator,
    update_indicator,
    delete_indicator,
    add_evidence,
)
from app.services.nist_service import record_nist_transition
from app.services.clock_service import get_clock_summary

router = APIRouter(prefix="/incidents", tags=["Incidents"])


@router.post("", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
def create_new_incident(
    incident_in: IncidentCreate,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """Create a new security incident with automated 72-hour regulatory deadline and audit trail."""
    actor = current_user.username if current_user else "system"
    incident = create_incident(db=db, incident_in=incident_in, actor=actor)
    return incident


@router.get("", response_model=IncidentListResponse)
def get_all_incidents(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    attack_type: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
):
    """List security incidents with optional filtering and pagination."""
    items, total = list_incidents(
        db=db,
        skip=skip,
        limit=limit,
        attack_type=attack_type,
        status_filter=status_filter,
    )
    return {"items": items, "total": total}


@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    """
    Retrieve full frontend-usable details for an incident:
    id, title, description, attack_type, status, priority, detected_at,
    deadline_at, source, affected assets, affected users, indicators,
    current NIST phase, timeline events, and evidence.
    """
    incident = get_incident_by_id(db, incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident #{incident_id} not found")
    return incident


@router.patch("/{incident_id}", response_model=IncidentResponse)
def update_incident_details(
    incident_id: int,
    incident_in: IncidentUpdate,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """
    Update incident properties. Validates state transitions, priority levels,
    and NIST phases. Every change appends an immutable timeline audit event.
    """
    incident = get_incident_by_id(db, incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident #{incident_id} not found")

    actor = current_user.username if current_user else "human"
    updated = update_incident(db=db, incident=incident, incident_in=incident_in, actor=actor)
    return updated


@router.delete("/{incident_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_incident(incident_id: int, db: Session = Depends(get_db)):
    """Delete an incident and all associated telemetry records."""
    success = delete_incident(db=db, incident_id=incident_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident #{incident_id} not found")
    return None


# ---------------------------------------------------------
# Indicators
# ---------------------------------------------------------

@router.get("/{incident_id}/indicators", response_model=List[IndicatorResponse])
def get_incident_indicators(incident_id: int, db: Session = Depends(get_db)):
    """Retrieve all indicators associated with the specified incident."""
    incident = get_incident_by_id(db, incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident #{incident_id} not found")
    return incident.indicators


@router.post("/{incident_id}/indicators", response_model=IndicatorResponse, status_code=status.HTTP_201_CREATED)
def create_incident_indicator(
    incident_id: int,
    indicator_in: IndicatorCreate,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """Add a new indicator to the incident and record it in the timeline."""
    actor = current_user.username if current_user else "human"
    return add_indicator(db=db, incident_id=incident_id, indicator_in=indicator_in, actor=actor)


@router.patch("/{incident_id}/indicators/{indicator_id}", response_model=IndicatorResponse)
def modify_incident_indicator(
    incident_id: int,
    indicator_id: int,
    indicator_in: IndicatorUpdate,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """Modify an existing indicator and record changes in the timeline."""
    actor = current_user.username if current_user else "human"
    return update_indicator(
        db=db,
        incident_id=incident_id,
        indicator_id=indicator_id,
        indicator_in=indicator_in,
        actor=actor,
    )


@router.delete("/{incident_id}/indicators/{indicator_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_incident_indicator(
    incident_id: int,
    indicator_id: int,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """Remove an indicator from the incident and audit the removal."""
    actor = current_user.username if current_user else "human"
    success = delete_indicator(db=db, incident_id=incident_id, indicator_id=indicator_id, actor=actor)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Indicator #{indicator_id} not found")
    return None


# ---------------------------------------------------------
# Timeline / Audit Log
# ---------------------------------------------------------

@router.get("/{incident_id}/timeline", response_model=List[TimelineEventResponse])
def get_incident_timeline(incident_id: int, db: Session = Depends(get_db)):
    """Retrieve chronological audit timeline events for the incident."""
    incident = get_incident_by_id(db, incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident #{incident_id} not found")
    return incident.timeline_events


# ---------------------------------------------------------
# NIST History
# ---------------------------------------------------------

@router.get("/{incident_id}/nist-history", response_model=List[NISTHistoryResponse])
def get_incident_nist_history(incident_id: int, db: Session = Depends(get_db)):
    """Retrieve all NIST IR phase transition history for the incident."""
    incident = get_incident_by_id(db, incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident #{incident_id} not found")
    return incident.nist_history


@router.post("/{incident_id}/nist-phase", response_model=NISTHistoryResponse)
def update_nist_phase(
    incident_id: int,
    req: NISTPhaseUpdate,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """Transition the incident to a new NIST IR phase and log rationale."""
    incident = get_incident_by_id(db, incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident #{incident_id} not found")

    actor = current_user.username if current_user else "human"
    entry = record_nist_transition(
        db=db,
        incident=incident,
        new_phase=req.phase,
        actor=actor,
        rationale=req.rationale,
        source="human",
    )
    db.commit()
    db.refresh(entry)
    return entry


# ---------------------------------------------------------
# Evidence
# ---------------------------------------------------------

@router.get("/{incident_id}/evidence", response_model=List[EvidenceResponse])
def get_incident_evidence(incident_id: int, db: Session = Depends(get_db)):
    """Retrieve all evidence metadata logged for the incident."""
    incident = get_incident_by_id(db, incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident #{incident_id} not found")
    return incident.evidence


@router.post("/{incident_id}/evidence", response_model=EvidenceResponse, status_code=status.HTTP_201_CREATED)
def create_incident_evidence(
    incident_id: int,
    evidence_in: EvidenceCreate,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """Log a new piece of evidence with SHA-256 integrity hash and collector details."""
    actor = current_user.username if current_user else evidence_in.collector
    return add_evidence(db=db, incident_id=incident_id, evidence_in=evidence_in, actor=actor)


# ---------------------------------------------------------
# Clock Summary
# ---------------------------------------------------------

@router.get("/{incident_id}/clock")
def get_incident_clock_status(incident_id: int, db: Session = Depends(get_db)):
    """Retrieve current countdown status against the 72-hour deadline."""
    incident = get_incident_by_id(db, incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident #{incident_id} not found")
    return get_clock_summary(detected_at=incident.detected_at, deadline_at=incident.deadline_at)


# ---------------------------------------------------------
# Affected Assets & Users
# ---------------------------------------------------------

@router.post("/{incident_id}/assets", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
def add_incident_asset(
    incident_id: int,
    asset_in: AssetCreate,
    db: Session = Depends(get_db),
):
    """Associate an affected system/asset with the incident."""
    incident = get_incident_by_id(db, incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident #{incident_id} not found")
    from datetime import datetime, timezone
    asset = IncidentAsset(
        incident_id=incident_id,
        asset_name=asset_in.asset_name,
        asset_type=asset_in.asset_type,
        description=asset_in.description,
        added_at=datetime.now(timezone.utc),
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


@router.post("/{incident_id}/affected-users", response_model=AffectedUserResponse, status_code=status.HTTP_201_CREATED)
def add_incident_user(
    incident_id: int,
    user_in: AffectedUserCreate,
    db: Session = Depends(get_db),
):
    """Associate an affected user with the incident."""
    incident = get_incident_by_id(db, incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident #{incident_id} not found")
    from datetime import datetime, timezone
    aff_user = IncidentUser(
        incident_id=incident_id,
        username=user_in.username,
        email=user_in.email,
        department=user_in.department,
        impact=user_in.impact,
        added_at=datetime.now(timezone.utc),
    )
    db.add(aff_user)
    db.commit()
    db.refresh(aff_user)
    return aff_user
