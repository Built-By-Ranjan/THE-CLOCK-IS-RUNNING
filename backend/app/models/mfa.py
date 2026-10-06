import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.db.database import Base, UTCDateTime


class MFAChallenge(Base):
    __tablename__ = "mfa_challenges"

    id = Column(Integer, primary_key=True, index=True)
    challenge_id = Column(
        String(64),
        unique=True,
        index=True,
        nullable=False,
        default=lambda: uuid.uuid4().hex,
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    otp_hash = Column(String(255), nullable=False)
    attempts = Column(Integer, default=0, nullable=False)
    max_attempts = Column(Integer, default=5, nullable=False)
    is_used = Column(Boolean, default=False, nullable=False)
    created_at = Column(
        UTCDateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    expires_at = Column(UTCDateTime, nullable=False)
    last_sent_at = Column(
        UTCDateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user = relationship("User")
