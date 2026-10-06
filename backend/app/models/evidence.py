from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base, UTCDateTime


class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(
        Integer,
        ForeignKey("incidents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    type = Column(String(100), nullable=False)  # e.g., Log, Disk Image, Memory Dump, Packet Capture, Email
    name = Column(String(255), nullable=False)
    source = Column(String(100), nullable=False)
    collected_at = Column(
        UTCDateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    collector = Column(String(100), nullable=False)
    sha256 = Column(String(64), nullable=True)
    status = Column(String(50), default="collected", nullable=False)  # collected, analyzed, archived
    details = Column(Text, nullable=True)
    created_at = Column(
        UTCDateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    incident = relationship("Incident", back_populates="evidence")
