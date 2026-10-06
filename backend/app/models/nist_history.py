from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base, UTCDateTime


class NISTHistory(Base):
    __tablename__ = "nist_history"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(
        Integer,
        ForeignKey("incidents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    phase = Column(String(100), nullable=False)  # Preparation, Detection & Analysis, Containment, Eradication & Recovery, Post-Incident Activity
    timestamp = Column(
        UTCDateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    actor = Column(String(100), nullable=False)
    rationale = Column(Text, nullable=True)

    incident = relationship("Incident", back_populates="nist_history")
