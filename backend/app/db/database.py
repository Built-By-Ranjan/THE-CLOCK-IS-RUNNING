from sqlalchemy import create_engine  # Import the SQLAlchemy engine factory.
from sqlalchemy.orm import declarative_base, sessionmaker  # Import ORM base and session helpers.

from app.core.config import settings  # Import application configuration.


engine = create_engine(settings.DATABASE_URL)  # Create the database engine from configuration.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)  # Configure database sessions.
Base = declarative_base()  # Create the declarative ORM base class.


def get_db():  # Define the database session dependency.
    db = SessionLocal()  # Open a new database session.
    try:  # Begin protected session usage.
        yield db  # Provide the session to the caller.
    finally:  # Ensure cleanup after session usage.
        db.close()  # Close the database session.
