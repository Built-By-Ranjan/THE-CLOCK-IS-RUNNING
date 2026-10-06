from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.db.database import Base


class IncidentUser(Base):  # Define an affected incident user.
    __tablename__ = "incident_users"  # Map the model to the affected-user table.

    id = Column(Integer, primary_key=True)  # Store the user association identifier.
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)  # Link the user to an incident.
    user_name = Column(String, nullable=False)  # Store the user name.
    user_identifier = Column(String)  # Store the user identifier.
    created_at = Column(  # Define the association creation timestamp.
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
