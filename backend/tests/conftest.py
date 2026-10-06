import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Set test environment
os.environ["SECRET_KEY"] = "test-secret-key-at-least-32-chars-long-123456"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app.main import app
from app.db.database import Base, get_db

# Create SQLite in-memory engine with StaticPool for test isolation
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client):
    # Register and login a standard test user
    client.post(
        "/auth/register",
        json={"username": "testsecanalyst", "email": "analyst@defense.corp", "password": "StrongPassword123!"},
    )
    login_resp = client.post(
        "/auth/login",
        json={"username": "testsecanalyst", "password": "StrongPassword123!"},
    )
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
