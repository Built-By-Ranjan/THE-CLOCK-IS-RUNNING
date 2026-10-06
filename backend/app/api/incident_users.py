from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.db.database import get_db
from app.schemas.incident_user import (
    IncidentUserCreate,
    IncidentUserResponse,
    IncidentUserUpdate,
)
from app.services.incident_service import get_incident
from app.services.incident_user_service import (
    create_incident_user,
    delete_incident_user,
    get_incident_user,
    list_incident_users,
    update_incident_user,
)


router = APIRouter(
    prefix="/incidents/{incident_id}/users",
    tags=["Affected Users"],
    dependencies=[Depends(get_current_user)],
)


def _require_incident(db: Session, incident_id: int) -> None:
    """Raise the standard error when an incident is missing."""
    if get_incident(db, incident_id) is None:
        raise HTTPException(status_code=404, detail="Incident not found")


@router.post(
    "", response_model=IncidentUserResponse, status_code=status.HTTP_201_CREATED
)
def create_incident_user_endpoint(
    incident_id: int,
    data: IncidentUserCreate,
    db: Session = Depends(get_db),
) -> IncidentUserResponse:
    """Create and return an affected user."""
    _require_incident(db, incident_id)
    return create_incident_user(db, incident_id, data)


@router.get("", response_model=list[IncidentUserResponse])
def list_incident_users_endpoint(
    incident_id: int, db: Session = Depends(get_db)
) -> list[IncidentUserResponse]:
    """Return all affected users for an incident."""
    _require_incident(db, incident_id)
    return list_incident_users(db, incident_id)


@router.patch("/{user_id}", response_model=IncidentUserResponse)
def update_incident_user_endpoint(
    incident_id: int,
    user_id: int,
    data: IncidentUserUpdate,
    db: Session = Depends(get_db),
) -> IncidentUserResponse:
    """Update and return an affected user."""
    _require_incident(db, incident_id)
    user = update_incident_user(db, incident_id, user_id, data)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_incident_user_endpoint(
    incident_id: int, user_id: int, db: Session = Depends(get_db)
) -> Response:
    """Delete an affected user."""
    _require_incident(db, incident_id)
    if not delete_incident_user(db, incident_id, user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
