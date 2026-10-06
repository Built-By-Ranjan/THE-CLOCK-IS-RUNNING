from typing import Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.api.deps import get_optional_current_user
from app.models.user import User
from app.schemas.simulation import SimulationResponse, SimulationCustomRequest
from app.services.simulation_service import (
    create_brute_force_simulation,
    create_ddos_simulation,
    create_phishing_simulation,
)

router = APIRouter(prefix="/simulations", tags=["Attack Simulations"])


@router.post("/brute-force", response_model=SimulationResponse, status_code=status.HTTP_201_CREATED)
def trigger_brute_force(
    req: Optional[SimulationCustomRequest] = None,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """
    Launch a controlled, safe Brute Force attack simulation.
    - Generates realistic security telemetry and safe indicators (RFC 5737 IP, usernames)
    - Persists incident in PostgreSQL
    - Starts the 72-hour regulatory countdown clock
    - Initializes NIST IR phase 'Detection & Analysis'
    - Creates timeline audit trail
    """
    actor = current_user.username if current_user else "simulator"
    params = req.model_dump() if req else {}
    incident = create_brute_force_simulation(db=db, actor=actor, custom_params=params)

    return {
        "incident_id": incident.id,
        "attack_type": incident.attack_type,
        "status": incident.status,
        "detected_at": incident.detected_at,
        "deadline_at": incident.deadline_at,
        "message": f"Controlled Brute Force simulation successfully initiated with Incident ID #{incident.id}.",
        "incident": incident,
    }


@router.post("/phishing", response_model=SimulationResponse, status_code=status.HTTP_201_CREATED)
def trigger_phishing(
    req: Optional[SimulationCustomRequest] = None,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """
    Launch a controlled, safe Phishing attack simulation.
    - Generates realistic email telemetry and safe indicators (mock domain, safe SHA-256)
    - Persists incident in PostgreSQL
    - Starts the 72-hour regulatory countdown clock
    - Initializes NIST IR phase 'Detection & Analysis'
    - Creates timeline audit trail
    """
    actor = current_user.username if current_user else "simulator"
    params = req.model_dump() if req else {}
    incident = create_phishing_simulation(db=db, actor=actor, custom_params=params)

    return {
        "incident_id": incident.id,
        "attack_type": incident.attack_type,
        "status": incident.status,
        "detected_at": incident.detected_at,
        "deadline_at": incident.deadline_at,
        "message": f"Controlled Phishing simulation successfully initiated with Incident ID #{incident.id}.",
        "incident": incident,
    }


@router.post("/ddos", response_model=SimulationResponse, status_code=status.HTTP_201_CREATED)
def trigger_ddos(
    req: Optional[SimulationCustomRequest] = None,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """Launch a controlled, safe DDoS attack simulation."""
    actor = current_user.username if current_user else "simulator"
    params = req.model_dump() if req else {}
    incident = create_ddos_simulation(db=db, actor=actor, custom_params=params)

    return {
        "incident_id": incident.id,
        "attack_type": incident.attack_type,
        "status": incident.status,
        "detected_at": incident.detected_at,
        "deadline_at": incident.deadline_at,
        "message": f"Controlled DDoS simulation successfully initiated with Incident ID #{incident.id}.",
        "incident": incident,
    }
