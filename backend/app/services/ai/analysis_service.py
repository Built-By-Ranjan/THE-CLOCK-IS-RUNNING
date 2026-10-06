from datetime import datetime, timezone
import logging
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.incident import Incident
from app.models.ai_analysis import AIAnalysis
from app.models.timeline import TimelineEvent
from app.schemas.ai import AIReviewRequest
from app.services.ai.gemini_service import gemini_service
from app.services.nist_service import record_nist_transition

logger = logging.getLogger(__name__)


def analyze_incident(
    db: Session,
    incident_id: int,
    actor: str = "AI",
) -> AIAnalysis:
    """
    Executes AI security analysis on the designated incident.
    Integrates Gemini AI with automated fallback and records audit timeline events.
    """
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise ValueError(f"Incident #{incident_id} not found")

    now = datetime.now(timezone.utc)

    # 1. Timeline event: AI Analysis Started
    start_event = TimelineEvent(
        incident_id=incident.id,
        timestamp=now,
        event="AI Analysis Started",
        actor=actor,
        source="AI",
        description=f"Automated AI security analysis started for incident #{incident.id}.",
    )
    db.add(start_event)
    db.flush()

    # 2. Prepare incident telemetry data
    incident_data = {
        "id": incident.id,
        "title": incident.title,
        "description": incident.description,
        "attack_type": incident.attack_type,
        "status": incident.status,
        "current_nist_phase": incident.current_nist_phase,
    }

    indicators_data = [
        {
            "id": ind.id,
            "indicator_type": getattr(ind, "type", getattr(ind, "indicator_type", "other")),
            "indicator_value": getattr(ind, "value", getattr(ind, "indicator_value", "")),
            "description": ind.description,
        }
        for ind in incident.indicators
    ]


    try:
        # 3. Call AI service
        ai_output, provider = gemini_service.analyze(incident_data, indicators_data)
    except Exception as exc:
        # Record failure in timeline
        db.add(TimelineEvent(
            incident_id=incident.id,
            timestamp=datetime.now(timezone.utc),
            event="AI Analysis Failed",
            actor=actor,
            source="AI",
            description=f"AI security analysis failed: {exc.__class__.__name__}.",
        ))
        db.commit()
        raise

    finish_time = datetime.now(timezone.utc)

    # 4. Persist AIAnalysis record
    analysis = AIAnalysis(
        incident_id=incident.id,
        incident_type=ai_output.incident_type,
        suggested_nist_phase=ai_output.suggested_nist_phase,
        suggested_severity=ai_output.suggested_severity,
        attack_technique=ai_output.attack_technique,
        attack_technique_name=ai_output.attack_technique_name,
        reason=ai_output.reason,
        recommended_actions=ai_output.recommended_actions,
        confidence=ai_output.confidence,
        disclaimer=ai_output.disclaimer,
        provider=provider,
        status="pending",
        decision=None,
        reviewed_by=None,
        reviewed_at=None,
        rejection_reason=None,
        override_values=None,
        created_at=finish_time,
    )
    db.add(analysis)
    db.flush()

    # 5. Timeline event: AI Analysis Completed & AI Suggestion
    completed_event = TimelineEvent(
        incident_id=incident.id,
        timestamp=finish_time,
        event="AI Analysis Completed",
        actor=actor,
        source="AI",
        description=(
            f"AI analysis completed via provider '{provider}'. "
            f"Suggested: {analysis.incident_type} ({analysis.attack_technique}), "
            f"NIST Phase: {analysis.suggested_nist_phase}, Severity: {analysis.suggested_severity}."
        ),
        new_value=analysis.attack_technique,
    )
    db.add(completed_event)

    suggestion_event = TimelineEvent(
        incident_id=incident.id,
        timestamp=finish_time,
        event="AI Suggestion Generated",
        actor=actor,
        source="AI",
        description=(
            f"AI suggestion generated: {analysis.incident_type} ({analysis.attack_technique}) "
            f"with severity '{analysis.suggested_severity}'. {analysis.disclaimer}"
        ),
        new_value=f"{analysis.incident_type} ({analysis.attack_technique})",
    )
    db.add(suggestion_event)

    db.commit()
    db.refresh(analysis)
    return analysis


def reanalyze_incident(
    db: Session,
    incident_id: int,
    actor: str = "analyst",
) -> AIAnalysis:
    """
    Triggers re-analysis for an incident.
    Strictly preserves all previous AI analysis records and generates a new AIAnalysis record.
    """
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise ValueError(f"Incident #{incident_id} not found")

    now = datetime.now(timezone.utc)

    # Timeline event: Re-analysis requested
    db.add(TimelineEvent(
        incident_id=incident.id,
        timestamp=now,
        event="AI Re-analysis Requested",
        actor=actor,
        source="human" if actor != "AI" else "AI",
        description=f"Re-analysis requested by '{actor}' for incident #{incident.id}.",
    ))
    db.flush()

    # Run analysis, creating a new AIAnalysis record
    return analyze_incident(db=db, incident_id=incident_id, actor="AI")


def get_incident_analyses(db: Session, incident_id: int) -> List[AIAnalysis]:
    """Retrieves all AI analysis records for an incident in descending chronological order."""
    return (
        db.query(AIAnalysis)
        .filter(AIAnalysis.incident_id == incident_id)
        .order_by(desc(AIAnalysis.created_at))
        .all()
    )


def get_incident_analysis_by_id(
    db: Session,
    incident_id: int,
    analysis_id: int,
) -> Optional[AIAnalysis]:
    """Retrieves a specific AI analysis by ID belonging to the specified incident."""
    return (
        db.query(AIAnalysis)
        .filter(AIAnalysis.id == analysis_id, AIAnalysis.incident_id == incident_id)
        .first()
    )


def review_incident_analysis(
    db: Session,
    incident_id: int,
    review_req: AIReviewRequest,
    actor: str = "security_analyst",
) -> AIAnalysis:
    """
    Processes human review decision (Accept, Reject, Override) for an AI analysis.
    Human decision is strictly authoritative.
    If NIST phase is accepted or overridden, updates incident phase using record_nist_transition.
    NOTE: Severity and Priority are completely independent. Priority is NEVER altered here.
    """
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise ValueError(f"Incident #{incident_id} not found")

    # Locate target analysis
    if review_req.analysis_id:
        analysis = (
            db.query(AIAnalysis)
            .filter(AIAnalysis.id == review_req.analysis_id, AIAnalysis.incident_id == incident_id)
            .first()
        )
    else:
        # Default to latest pending or latest overall analysis
        analysis = (
            db.query(AIAnalysis)
            .filter(AIAnalysis.incident_id == incident_id, AIAnalysis.status == "pending")
            .order_by(desc(AIAnalysis.created_at))
            .first()
        )
        if not analysis:
            analysis = (
                db.query(AIAnalysis)
                .filter(AIAnalysis.incident_id == incident_id)
                .order_by(desc(AIAnalysis.created_at))
                .first()
            )

    if not analysis:
        raise ValueError(f"No AI analysis found to review for incident #{incident_id}")

    decision = review_req.decision.lower()
    now = datetime.now(timezone.utc)

    if decision == "accept":
        analysis.status = "accepted"
        analysis.decision = "accept"
        analysis.reviewed_by = actor
        analysis.reviewed_at = now

        # Human Accept timeline event
        db.add(TimelineEvent(
            incident_id=incident.id,
            timestamp=now,
            event="AI Suggestion Accepted",
            actor=actor,
            source="human",
            description=f"Human reviewer '{actor}' accepted AI analysis #{analysis.id} suggestions.",
            new_value=analysis.attack_technique,
        ))

        if review_req.apply_to_incident:
            # Transition NIST phase using existing Core-1 mechanism if different
            if analysis.suggested_nist_phase and analysis.suggested_nist_phase != incident.current_nist_phase:
                record_nist_transition(
                    db=db,
                    incident=incident,
                    new_phase=analysis.suggested_nist_phase,
                    actor=actor,
                    rationale=f"Accepted AI suggestion: {analysis.suggested_nist_phase}",
                    source="human",
                )
            if analysis.incident_type:
                incident.attack_type = analysis.incident_type

    elif decision == "reject":
        analysis.status = "rejected"
        analysis.decision = "reject"
        analysis.reviewed_by = actor
        analysis.reviewed_at = now
        analysis.rejection_reason = review_req.rejection_reason or "Rejected by reviewer without comment."

        # Human Reject timeline event
        db.add(TimelineEvent(
            incident_id=incident.id,
            timestamp=now,
            event="AI Suggestion Rejected",
            actor=actor,
            source="human",
            description=f"Human reviewer '{actor}' rejected AI analysis #{analysis.id}."
            + (f" Reason: {analysis.rejection_reason}" if analysis.rejection_reason else ""),
            previous_value=analysis.attack_technique,
        ))

    elif decision == "override":
        analysis.status = "overridden"
        analysis.decision = "override"
        analysis.reviewed_by = actor
        analysis.reviewed_at = now
        analysis.override_values = review_req.override_values or {}

        # Human Override timeline event
        db.add(TimelineEvent(
            incident_id=incident.id,
            timestamp=now,
            event="AI Suggestion Overridden",
            actor=actor,
            source="human",
            description=f"Human reviewer '{actor}' overrode AI analysis #{analysis.id} with custom values.",
            previous_value=analysis.attack_technique,
            new_value=str(analysis.override_values),
        ))

        if review_req.apply_to_incident and analysis.override_values:
            override_nist = analysis.override_values.get("suggested_nist_phase") or analysis.override_values.get("nist_phase")
            if override_nist and override_nist != incident.current_nist_phase:
                record_nist_transition(
                    db=db,
                    incident=incident,
                    new_phase=override_nist,
                    actor=actor,
                    rationale=f"Analyst override to {override_nist}",
                    source="human",
                )
            override_type = analysis.override_values.get("incident_type") or analysis.override_values.get("attack_type")
            if override_type:
                incident.attack_type = override_type

    else:
        raise ValueError(f"Unsupported review decision '{review_req.decision}'. Allowed: accept, reject, override")

    db.commit()
    db.refresh(analysis)
    return analysis
