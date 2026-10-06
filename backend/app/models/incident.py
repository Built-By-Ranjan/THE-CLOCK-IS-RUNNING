from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.db.database import Base, UTCDateTime


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    attack_type = Column(String(100), nullable=False)  # "Brute Force", "Phishing", etc.
    status = Column(String(50), nullable=False, default="Open")  # Open -> Under Investigation -> Contained -> Eradicated -> Recovered -> Closed
    priority = Column(String(10), nullable=False, default="P3")  # P1, P2, P3, P4
    source = Column(String(100), nullable=False, default="simulator")  # simulator, system, human, AI
    current_nist_phase = Column(String(100), nullable=False, default="Detection & Analysis")

    detected_at = Column(
        UTCDateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    deadline_at = Column(
        UTCDateTime,
        nullable=False,
    )

    created_at = Column(
        UTCDateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        UTCDateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    indicators = relationship(
        "Indicator",
        back_populates="incident",
        cascade="all, delete-orphan",
        order_by="Indicator.created_at",
    )
    timeline_events = relationship(
        "TimelineEvent",
        back_populates="incident",
        cascade="all, delete-orphan",
        order_by="TimelineEvent.timestamp",
    )
    nist_history = relationship(
        "NISTHistory",
        back_populates="incident",
        cascade="all, delete-orphan",
        order_by="NISTHistory.timestamp",
    )
    affected_assets = relationship(
        "IncidentAsset",
        back_populates="incident",
        cascade="all, delete-orphan",
        order_by="IncidentAsset.added_at",
    )
    affected_users = relationship(
        "IncidentUser",
        back_populates="incident",
        cascade="all, delete-orphan",
        order_by="IncidentUser.added_at",
    )
    evidence = relationship(
        "Evidence",
        back_populates="incident",
        cascade="all, delete-orphan",
        order_by="Evidence.created_at",
    )
