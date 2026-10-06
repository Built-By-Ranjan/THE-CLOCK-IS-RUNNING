from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.api.auth import get_current_user
from app.schemas.incident import IncidentCreate, IncidentResponse, IncidentUpdate
from app.schemas.nist import NistHistoryResponse, NistPhaseChange
from app.schemas.timeline import TimelineEventResponse
from app.services.incident_service import (
    create_incident,
    get_incident,
    list_incidents,
    update_incident,
)
from app.services.status_service import InvalidStatusTransition
from app.services.nist_service import (
    InvalidNistPhase,
    change_nist_phase,
    list_nist_history,
)
from app.services.timeline_service import get_timeline


router = APIRouter(
    prefix="/incidents",
    tags=["Incidents"],
    dependencies=[Depends(get_current_user)],
)


@router.post("", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
def create_incident_endpoint(
    data: IncidentCreate, db: Session = Depends(get_db)
) -> IncidentResponse:
    """Create and return an incident."""
    return create_incident(db, data)


@router.get("", response_model=list[IncidentResponse])
def list_incidents_endpoint(db: Session = Depends(get_db)) -> list[IncidentResponse]:
    """Return all incidents newest first."""
    return list_incidents(db)


@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident_endpoint(
    incident_id: int, db: Session = Depends(get_db)
) -> IncidentResponse:
    """Return one incident or a not-found error."""
    incident = get_incident(db, incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.patch("/{incident_id}", response_model=IncidentResponse)
def update_incident_endpoint(
    incident_id: int, data: IncidentUpdate, db: Session = Depends(get_db)
) -> IncidentResponse:
    """Update and return one incident."""
    try:
        incident = update_incident(db, incident_id, data)
    except InvalidStatusTransition as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.patch("/{incident_id}/nist-phase", response_model=IncidentResponse)
def change_incident_nist_phase(
    incident_id: int, data: NistPhaseChange, db: Session = Depends(get_db)
) -> IncidentResponse:
    """Change an incident's NIST phase and return the incident."""
    incident = get_incident(db, incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    try:
        return change_nist_phase(db, incident, data.new_phase, data.reason)
    except InvalidNistPhase as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.get(
    "/{incident_id}/nist-history",
    response_model=list[NistHistoryResponse],
)
def get_incident_nist_history(
    incident_id: int, db: Session = Depends(get_db)
) -> list[NistHistoryResponse]:
    """Return an incident's NIST phase history."""
    if get_incident(db, incident_id) is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return list_nist_history(db, incident_id)


@router.get("/{incident_id}/timeline", response_model=list[TimelineEventResponse])
def get_incident_timeline(
    incident_id: int, db: Session = Depends(get_db)
) -> list[TimelineEventResponse]:
    """Return an incident timeline from oldest to newest."""
    if get_incident(db, incident_id) is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return get_timeline(db, incident_id)
