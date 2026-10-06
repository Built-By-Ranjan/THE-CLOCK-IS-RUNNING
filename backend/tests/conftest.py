import os
import tempfile
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


# Configure the application with an isolated SQLite database before importing it.
_database_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_database_file.close()
os.environ["DATABASE_URL"] = f"sqlite:///{_database_file.name}"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-with-at-least-32-bytes"

from app.core.security import hash_password
from app.db.database import Base, get_db
from app.main import app
from app.models.user import User


TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False)
test_engine = create_engine(os.environ["DATABASE_URL"])
TestingSessionLocal.configure(bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def test_database() -> Generator[None, None, None]:
    """Create and remove all tables in the isolated test database."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()
    os.unlink(_database_file.name)


@pytest.fixture
def db_session(test_database: None) -> Generator[Session, None, None]:
    """Provide a database session for test setup."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        for table in reversed(Base.metadata.sorted_tables):
            db.execute(table.delete())
        db.commit()
        db.close()


@pytest.fixture
def client(test_database: None) -> Generator[TestClient, None, None]:
    """Use test sessions for every application database request."""
    def override_get_db() -> Generator[Session, None, None]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(
    client: TestClient, db_session: Session
) -> dict[str, str]:
    """Create a test user and obtain a real login token."""
    user = User(email="test@example.com", password_hash=hash_password("password"))
    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "password"},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}
