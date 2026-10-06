from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String

from app.db.database import Base


class User(Base):  # Define the user database model.
    __tablename__ = "users"  # Map the model to the users table.

    id = Column(Integer, primary_key=True)  # Store the unique user identifier.
    email = Column(String, unique=True, nullable=False)  # Store the user's unique email.
    password_hash = Column(String, nullable=False)  # Store the bcrypt password hash.
    created_at = Column(  # Define the account creation timestamp.
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
