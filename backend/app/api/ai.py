from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.api.deps import get_optional_current_user
from app.models.user import User
from app.schemas.ai import (
    AIAnalysisResponse,
    AIReviewRequest,
)
from app.services.ai.analysis_service import (
    analyze_incident,
    reanalyze_incident,
    get_incident_analyses,
    get_incident_analysis_by_id,
    review_incident_analysis,
)

router = APIRouter(prefix="/incidents", tags=["AI Incident Intelligence"])


@router.post(
    "/{incident_id}/ai/analyze",
    response_model=AIAnalysisResponse,
    status_code=status.HTTP_201_CREATED,
)
def run_incident_ai_analysis(
    incident_id: int,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """
    Triggers automated AI security analysis for the incident.
    Integrates Gemini AI with automated knowledge base reference and controlled fallback.
    Appends audit events to the incident timeline.
    """
    actor = current_user.username if current_user else "AI"
    try:
        return analyze_incident(db=db, incident_id=incident_id, actor=actor)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI analysis execution failed: {e}",
        )


@router.get(
    "/{incident_id}/ai/analyses",
    response_model=List[AIAnalysisResponse],
)
def list_incident_ai_analyses(
    incident_id: int,
    db: Session = Depends(get_db),
):
    """
    Retrieves all AI analysis records generated for an incident in descending chronological order.
    """
    return get_incident_analyses(db=db, incident_id=incident_id)


@router.get(
    "/{incident_id}/ai/analysis/{analysis_id}",
    response_model=AIAnalysisResponse,
)
def get_incident_ai_analysis(
    incident_id: int,
    analysis_id: int,
    db: Session = Depends(get_db),
):
    """
    Retrieves a specific AI analysis record for the incident.
    """
    analysis = get_incident_analysis_by_id(db=db, incident_id=incident_id, analysis_id=analysis_id)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"AI Analysis #{analysis_id} not found for incident #{incident_id}",
        )
    return analysis


@router.post(
    "/{incident_id}/ai/reanalyze",
    response_model=AIAnalysisResponse,
    status_code=status.HTTP_201_CREATED,
)
def run_incident_ai_reanalysis(
    incident_id: int,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """
    Re-analyzes the incident with updated telemetry and indicators.
    Strictly preserves all previous AI analysis records and persists a new analysis record.
    """
    actor = current_user.username if current_user else "analyst"
    try:
        return reanalyze_incident(db=db, incident_id=incident_id, actor=actor)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI re-analysis execution failed: {e}",
        )


@router.post(
    "/{incident_id}/ai/review",
    response_model=AIAnalysisResponse,
)
def submit_ai_human_review(
    incident_id: int,
    review_req: AIReviewRequest,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """
    Submits human analyst decision (Accept, Reject, or Override) for an AI suggestion.
    Human decisions are strictly authoritative.
    If NIST phase transition is accepted or overridden, updates incident phase via record_nist_transition.
    Logs human decision audit event in timeline.
    """
    actor = current_user.username if current_user else "security_analyst"
    try:
        return review_incident_analysis(
            db=db,
            incident_id=incident_id,
            review_req=review_req,
            actor=actor,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to process review: {e}",
        )
