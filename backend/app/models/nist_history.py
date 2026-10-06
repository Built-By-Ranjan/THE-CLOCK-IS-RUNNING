from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text

from app.db.database import Base


class NistHistory(Base):  # Store each NIST phase change for an incident.
    __tablename__ = "nist_history"

    id = Column(Integer, primary_key=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False, index=True)
    previous_phase = Column(String, nullable=False)
    new_phase = Column(String, nullable=False)
    actor = Column(String, nullable=False)
    reason = Column(Text)
    timestamp = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
