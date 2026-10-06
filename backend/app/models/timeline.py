from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text

from app.db.database import Base


class TimelineEvent(Base):  # Define an incident timeline event.
    __tablename__ = "timeline_events"  # Map the model to the timeline table.

    id = Column(Integer, primary_key=True)  # Store the event identifier.
    incident_id = Column(  # Link the event to its incident.
        Integer, ForeignKey("incidents.id"), nullable=False, index=True
    )
    timestamp = Column(  # Store when the event occurred.
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    event_type = Column(String, nullable=False)  # Store the event type.
    actor = Column(String)  # Store who or what caused the event.
    source_type = Column(String, nullable=False)  # Store the event source category.
    previous_value = Column(Text)  # Store the previous field value.
    new_value = Column(Text)  # Store the new field value.
    description = Column(Text)  # Store the event description.
