from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base, UTCDateTime


class TimelineEvent(Base):
    __tablename__ = "timeline_events"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(
        Integer,
        ForeignKey("incidents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    timestamp = Column(
        UTCDateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    event = Column(String(255), nullable=False)
    actor = Column(String(100), nullable=False)
    source = Column(String(50), nullable=False)  # simulator, system, human, AI
    description = Column(Text, nullable=False)
    previous_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)

    incident = relationship("Incident", back_populates="timeline_events")
