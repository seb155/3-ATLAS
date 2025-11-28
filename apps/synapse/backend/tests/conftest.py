"""
Pytest configuration and shared fixtures for backend tests.
Uses PostgreSQL database for all tests (no SQLite).
"""
import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app

# PostgreSQL test database URL
# Use localhost:5433 when running from host, workspace-postgres:5432 when in Docker
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5433/synapse_test"
)


@pytest.fixture(scope="session")
def engine():
    """Create a test database engine (session-scoped for performance)."""
    engine = create_engine(
        TEST_DATABASE_URL,
        poolclass=StaticPool,
        echo=False
    )

    # Drop existing tables first (in case schema changed)
    Base.metadata.drop_all(bind=engine)

    # Create all tables with current schema
    Base.metadata.create_all(bind=engine)

    yield engine

    # Drop all tables after tests
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(engine):
    """Create a new database session for each test function."""
    connection = engine.connect()
    transaction = connection.begin()

    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database session override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def reset_db(db_session):
    """Clean database before test (opt-in only)."""
    # Truncate all tables before each test
    for table in reversed(Base.metadata.sorted_tables):
        db_session.execute(table.delete())
    db_session.commit()

    yield

    # Cleanup after test
    db_session.rollback()
