from fastapi import APIRouter, Depends  # Import FastAPI routing and dependencies.
from sqlalchemy.orm import Session  # Import the SQLAlchemy session type.

from app.db.database import get_db  # Import the database session dependency.
from app.models.indicator import Indicator  # Import the indicator model.
from app.services.simulation_service import create_brute_force_simulation, create_phishing_simulation  # Import simulation services.


router = APIRouter(prefix="/simulations", tags=["Simulations"])  # Create the simulations router.


@router.post("/brute-force")  # Expose the brute-force simulation endpoint.
def brute_force_simulation(db: Session = Depends(get_db)):  # Create and return a brute-force simulation.
    incident = create_brute_force_simulation(db)  # Create the simulated incident and indicators.
    indicators = db.query(Indicator).filter(Indicator.incident_id == incident.id).all()  # Load its indicators.

    return {  # Return the simulation summary.
        "id": incident.id,  # Include the incident identifier.
        "title": incident.title,  # Include the incident title.
        "attack_type": incident.attack_type,  # Include the attack type.
        "status": incident.status,  # Include the incident status.
        "nist_phase": incident.nist_phase,  # Include the NIST phase.
        "detected_at": incident.detected_at,  # Include the detection timestamp.
        "deadline_at": incident.deadline_at,  # Include the response deadline.
        "indicators": [  # Include the incident indicators.
            {  # Serialize one indicator.
                "type": indicator.type,  # Include the indicator type.
                "value": indicator.value,  # Include the indicator value.
                "note": indicator.note,  # Include the indicator note.
            }
            for indicator in indicators
        ],
    }


@router.post("/phishing")  # Expose the phishing simulation endpoint.
def phishing_simulation(db: Session = Depends(get_db)):  # Create and return a phishing simulation.
    incident = create_phishing_simulation(db)  # Create the simulated incident and indicators.
    indicators = db.query(Indicator).filter(Indicator.incident_id == incident.id).all()  # Load its indicators.

    return {  # Return the simulation summary.
        "id": incident.id,  # Include the incident identifier.
        "title": incident.title,  # Include the incident title.
        "attack_type": incident.attack_type,  # Include the attack type.
        "status": incident.status,  # Include the incident status.
        "nist_phase": incident.nist_phase,  # Include the NIST phase.
        "detected_at": incident.detected_at,  # Include the detection timestamp.
        "deadline_at": incident.deadline_at,  # Include the response deadline.
        "indicators": [  # Include the incident indicators.
            {  # Serialize one indicator.
                "type": indicator.type,  # Include the indicator type.
                "value": indicator.value,  # Include the indicator value.
                "note": indicator.note,  # Include the indicator note.
            }
            for indicator in indicators
        ],
    }
