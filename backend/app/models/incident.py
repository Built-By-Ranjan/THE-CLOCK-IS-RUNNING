from datetime import datetime, timezone  # Import timezone-aware timestamp helpers.

from sqlalchemy import Column, DateTime, Integer, String, Text  # Import SQLAlchemy column types.

from app.db.database import Base  # Import the shared declarative base.


class Incident(Base):  # Define the incident database model.
    __tablename__ = "incidents"  # Map the model to the incidents table.

    id = Column(Integer, primary_key=True)  # Store the unique incident identifier.
    title = Column(String, nullable=False)  # Store the incident title.
    description = Column(Text)  # Store the incident description.
    what_happened = Column(Text)  # Store the incident narrative.
    source = Column(String)  # Store the incident source.
    initial_impact = Column(Text)  # Store the initial impact assessment.
    attack_type = Column(String)  # Store the attack classification.
    severity = Column(String, default="Not Determined")  # Store the incident severity.
    nist_phase = Column(String, default="Detection & Analysis")  # Store the NIST response phase.
    status = Column(String, default="Open")  # Store the incident status.
    notes = Column(Text)  # Store additional incident notes.
    detected_at = Column(DateTime(timezone=True))  # Store when the incident was detected.
    deadline_at = Column(DateTime(timezone=True))  # Store the incident response deadline.
    created_at = Column(  # Define the incident creation timestamp.
        DateTime(timezone=True),  # Store the creation time with timezone information.
        default=lambda: datetime.now(timezone.utc),  # Set the creation time in UTC.
    )
    updated_at = Column(  # Define the incident update timestamp.
        DateTime(timezone=True),  # Store the update time with timezone information.
        default=lambda: datetime.now(timezone.utc),  # Set the initial update time in UTC.
        onupdate=lambda: datetime.now(timezone.utc),  # Refresh the update time in UTC.
    )
