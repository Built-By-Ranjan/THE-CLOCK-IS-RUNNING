from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base, UTCDateTime


class IncidentAsset(Base):
    __tablename__ = "incident_assets"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(
        Integer,
        ForeignKey("incidents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    asset_name = Column(String(255), nullable=False)
    asset_type = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    added_at = Column(
        UTCDateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    incident = relationship("Incident", back_populates="affected_assets")


class IncidentUser(Base):
    __tablename__ = "incident_users"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(
        Integer,
        ForeignKey("incidents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    username = Column(String(100), nullable=False)
    email = Column(String(255), nullable=True)
    department = Column(String(100), nullable=True)
    impact = Column(Text, nullable=True)
    added_at = Column(
        UTCDateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    incident = relationship("Incident", back_populates="affected_users")
