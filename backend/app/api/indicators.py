from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.db.database import get_db
from app.schemas.indicator import (
    IndicatorCreate,
    IndicatorResponse,
    IndicatorUpdate,
)
from app.services.incident_service import get_incident
from app.services.indicator_service import (
    create_indicator,
    delete_indicator,
    get_indicator,
    list_indicators,
    update_indicator,
)


router = APIRouter(
    prefix="/incidents/{incident_id}/indicators",
    tags=["Indicators"],
    dependencies=[Depends(get_current_user)],
)


def _require_incident(db: Session, incident_id: int) -> None:
    """Raise the standard error when an incident is missing."""
    if get_incident(db, incident_id) is None:
        raise HTTPException(status_code=404, detail="Incident not found")


@router.post("", response_model=IndicatorResponse, status_code=status.HTTP_201_CREATED)
def create_indicator_endpoint(
    incident_id: int,
    data: IndicatorCreate,
    db: Session = Depends(get_db),
) -> IndicatorResponse:
    """Create and return an incident indicator."""
    _require_incident(db, incident_id)
    return create_indicator(db, incident_id, data)


@router.get("", response_model=list[IndicatorResponse])
def list_indicators_endpoint(
    incident_id: int, db: Session = Depends(get_db)
) -> list[IndicatorResponse]:
    """Return all indicators for an incident."""
    _require_incident(db, incident_id)
    return list_indicators(db, incident_id)


@router.patch("/{indicator_id}", response_model=IndicatorResponse)
def update_indicator_endpoint(
    incident_id: int,
    indicator_id: int,
    data: IndicatorUpdate,
    db: Session = Depends(get_db),
) -> IndicatorResponse:
    """Update and return an incident indicator."""
    _require_incident(db, incident_id)
    indicator = update_indicator(db, incident_id, indicator_id, data)
    if indicator is None:
        raise HTTPException(status_code=404, detail="Indicator not found")
    return indicator


@router.delete("/{indicator_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_indicator_endpoint(
    incident_id: int, indicator_id: int, db: Session = Depends(get_db)
) -> Response:
    """Delete an incident indicator."""
    _require_incident(db, incident_id)
    if not delete_indicator(db, incident_id, indicator_id):
        raise HTTPException(status_code=404, detail="Indicator not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
