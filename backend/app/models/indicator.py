from datetime import datetime, timezone  # Import timezone-aware timestamp helpers.

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text  # Import SQLAlchemy column types.

from app.db.database import Base  # Import the shared declarative base.


class Indicator(Base):  # Define the indicator database model.
    __tablename__ = "indicators"  # Map the model to the indicators table.

    id = Column(Integer, primary_key=True)  # Store the unique indicator identifier.
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)  # Link the indicator to an incident.
    type = Column(String)  # Store the indicator type.
    value = Column(String)  # Store the indicator value.
    note = Column(Text)  # Store the indicator note.
    created_at = Column(  # Define the indicator creation timestamp.
        DateTime(timezone=True),  # Store the creation time with timezone information.
        default=lambda: datetime.now(timezone.utc),  # Set the creation time in UTC.
    )
    updated_at = Column(  # Define the indicator update timestamp.
        DateTime(timezone=True),  # Store the update time with timezone information.
        default=lambda: datetime.now(timezone.utc),  # Set the initial update time in UTC.
        onupdate=lambda: datetime.now(timezone.utc),  # Refresh the update time in UTC.
    )
