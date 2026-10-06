from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base, UTCDateTime


class AIAnalysis(Base):
    __tablename__ = "ai_analyses"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(
        Integer,
        ForeignKey("incidents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # AI Suggestions
    incident_type = Column(String(100), nullable=False)
    suggested_nist_phase = Column(String(100), nullable=False)
    suggested_severity = Column(String(50), nullable=False)  # "Low", "Medium", "High", "Critical", "Not Determined"
    attack_technique = Column(String(50), nullable=False)  # e.g. "T1110", "T1566", etc.
    attack_technique_name = Column(String(255), nullable=True)
    reason = Column(Text, nullable=False)
    recommended_actions = Column(JSON, nullable=False, default=list)  # list of strings
    confidence = Column(Float, nullable=True, default=0.85)
    disclaimer = Column(
        String(255),
        nullable=False,
        default="AI Suggested — Human Review Required",
    )
    provider = Column(String(50), nullable=False, default="gemini")  # "gemini" or "fallback"

    # Human Review state
    status = Column(String(50), nullable=False, default="pending")  # "pending", "accepted", "rejected", "overridden"
    decision = Column(String(50), nullable=True)  # "accept", "reject", "override"
    reviewed_by = Column(String(100), nullable=True)
    reviewed_at = Column(UTCDateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    override_values = Column(JSON, nullable=True)  # dictionary of overridden values if applicable

    created_at = Column(
        UTCDateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    incident = relationship("Incident", back_populates="ai_analyses")
