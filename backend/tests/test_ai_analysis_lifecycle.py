from datetime import datetime, timezone
import pytest
from sqlalchemy.orm import Session

from app.models.incident import Incident
from app.models.indicator import Indicator
from app.models.ai_analysis import AIAnalysis
from app.models.timeline import TimelineEvent
from app.models.nist_history import NISTHistory
from app.schemas.incident import IncidentCreate
from app.schemas.ai import AIReviewRequest
from app.services.incident_service import create_incident
from app.services.ai.analysis_service import (
    analyze_incident,
    reanalyze_incident,
    get_incident_analyses,
    get_incident_analysis_by_id,
    review_incident_analysis,
)


@pytest.fixture
def sample_incident(db: Session) -> Incident:
    inc_in = IncidentCreate(
        title="Unauthorized SSH Access Attempts",
        description="Over 300 failed SSH logins detected from external IP 198.51.100.42 within 10 minutes.",
        attack_type="Brute Force",
        priority="P2",
    )
    inc = create_incident(db=db, incident_in=inc_in, actor="test_user")
    
    # Add an indicator
    ind = Indicator(
        incident_id=inc.id,
        type="ip",
        value="198.51.100.42",
        description="External source IP performing SSH brute force",
    )

    db.add(ind)
    db.commit()
    db.refresh(inc)
    return inc


def test_ai_analysis_creation_and_timeline(db: Session, sample_incident: Incident):
    """Verify AI analysis creation, default pending state, and timeline logging."""
    analysis = analyze_incident(db=db, incident_id=sample_incident.id, actor="test_analyst")

    assert analysis.id is not None
    assert analysis.incident_id == sample_incident.id
    assert analysis.status == "pending"
    assert analysis.decision is None
    assert analysis.incident_type == "Brute Force"
    assert analysis.attack_technique == "T1110"
    assert analysis.suggested_severity == "High"
    assert analysis.disclaimer == "AI Suggested — Human Review Required"

    # Verify timeline events: AI Analysis Started, AI Analysis Completed, AI Suggestion Generated
    timeline = db.query(TimelineEvent).filter(TimelineEvent.incident_id == sample_incident.id).all()
    events = [t.event for t in timeline]
    assert "AI Analysis Started" in events
    assert "AI Analysis Completed" in events
    assert "AI Suggestion Generated" in events


def test_reanalysis_retention(db: Session, sample_incident: Incident):
    """Verify that re-analysis creates a new record and never overwrites prior analyses."""
    first_analysis = analyze_incident(db=db, incident_id=sample_incident.id)
    first_id = first_analysis.id

    second_analysis = reanalyze_incident(db=db, incident_id=sample_incident.id, actor="lead_analyst")
    second_id = second_analysis.id

    assert first_id != second_id

    # Retrieve all analyses
    all_analyses = get_incident_analyses(db=db, incident_id=sample_incident.id)
    assert len(all_analyses) == 2
    ids = [a.id for a in all_analyses]
    assert first_id in ids
    assert second_id in ids

    # Timeline event for re-analysis
    reanalysis_events = (
        db.query(TimelineEvent)
        .filter(TimelineEvent.incident_id == sample_incident.id, TimelineEvent.event == "AI Re-analysis Requested")
        .all()
    )
    assert len(reanalysis_events) == 1


def test_human_accept_decision_and_nist_transition(db: Session, sample_incident: Incident):
    """Verify accepting AI suggestion transitions NIST phase via record_nist_transition and logs audit event."""
    # Ensure current phase is different from suggestion to test transition
    sample_incident.current_nist_phase = "Preparation"
    db.commit()

    analysis = analyze_incident(db=db, incident_id=sample_incident.id)

    review_req = AIReviewRequest(
        analysis_id=analysis.id,
        decision="accept",
        apply_to_incident=True,
    )
    reviewed = review_incident_analysis(
        db=db,
        incident_id=sample_incident.id,
        review_req=review_req,
        actor="soc_lead",
    )

    assert reviewed.status == "accepted"
    assert reviewed.decision == "accept"
    assert reviewed.reviewed_by == "soc_lead"
    assert reviewed.reviewed_at is not None

    # Verify incident phase was updated via existing NIST mechanism
    db.refresh(sample_incident)
    assert sample_incident.current_nist_phase == analysis.suggested_nist_phase

    # Verify NISTHistory record exists
    history = db.query(NISTHistory).filter(NISTHistory.incident_id == sample_incident.id).all()
    assert any(h.phase == analysis.suggested_nist_phase for h in history)

    # Verify timeline event: AI Suggestion Accepted
    timeline = db.query(TimelineEvent).filter(TimelineEvent.incident_id == sample_incident.id).all()
    events = [t.event for t in timeline]
    assert "AI Suggestion Accepted" in events


def test_human_reject_decision(db: Session, sample_incident: Incident):
    """Verify rejecting AI suggestion records status, rejection reason, and timeline event."""
    analysis = analyze_incident(db=db, incident_id=sample_incident.id)

    review_req = AIReviewRequest(
        analysis_id=analysis.id,
        decision="reject",
        rejection_reason="Telemetry indicates benign scanner activity, not brute force.",
        apply_to_incident=True,
    )
    reviewed = review_incident_analysis(
        db=db,
        incident_id=sample_incident.id,
        review_req=review_req,
        actor="senior_analyst",
    )

    assert reviewed.status == "rejected"
    assert reviewed.decision == "reject"
    assert reviewed.reviewed_by == "senior_analyst"
    assert "benign scanner" in reviewed.rejection_reason

    # Verify timeline event: AI Suggestion Rejected
    timeline = db.query(TimelineEvent).filter(TimelineEvent.incident_id == sample_incident.id).all()
    events = [t.event for t in timeline]
    assert "AI Suggestion Rejected" in events


def test_human_override_decision(db: Session, sample_incident: Incident):
    """Verify overriding AI suggestion applies custom values and logs audit event."""
    analysis = analyze_incident(db=db, incident_id=sample_incident.id)

    override_values = {
        "incident_type": "PowerShell Execution",
        "attack_technique": "T1059.001",
        "suggested_nist_phase": "Containment, Eradication & Recovery",
        "suggested_severity": "Critical",
    }
    review_req = AIReviewRequest(
        analysis_id=analysis.id,
        decision="override",
        override_values=override_values,
        apply_to_incident=True,
    )
    reviewed = review_incident_analysis(
        db=db,
        incident_id=sample_incident.id,
        review_req=review_req,
        actor="incident_commander",
    )

    assert reviewed.status == "overridden"
    assert reviewed.decision == "override"
    assert reviewed.override_values == override_values

    # Verify incident NIST phase updated to overridden phase
    db.refresh(sample_incident)
    assert sample_incident.current_nist_phase == "Containment, Eradication & Recovery"
    assert sample_incident.attack_type == "PowerShell Execution"

    # Verify timeline event: AI Suggestion Overridden
    timeline = db.query(TimelineEvent).filter(TimelineEvent.incident_id == sample_incident.id).all()
    events = [t.event for t in timeline]
    assert "AI Suggestion Overridden" in events


def test_severity_independent_from_priority(db: Session, sample_incident: Incident):
    """
    CRITICAL BUSINESS RULE:
    Severity and Priority are COMPLETELY INDEPENDENT.
    Priority must NOT be modified by AI analysis, Accept, Reject, or Override.
    """
    initial_priority = sample_incident.priority
    assert initial_priority == "P2"

    # 1. AI analysis performed
    analysis = analyze_incident(db=db, incident_id=sample_incident.id)
    assert analysis.suggested_severity == "High"
    db.refresh(sample_incident)
    assert sample_incident.priority == "P2"  # Priority untouched

    # 2. Human Accept
    review_incident_analysis(
        db=db,
        incident_id=sample_incident.id,
        review_req=AIReviewRequest(decision="accept"),
        actor="analyst",
    )
    db.refresh(sample_incident)
    assert sample_incident.priority == "P2"  # Priority untouched

    # 3. Human Override with Critical severity
    review_incident_analysis(
        db=db,
        incident_id=sample_incident.id,
        review_req=AIReviewRequest(
            decision="override",
            override_values={"suggested_severity": "Critical"},
        ),
        actor="analyst",
    )
    db.refresh(sample_incident)
    assert sample_incident.priority == "P2"  # Priority still untouched!
