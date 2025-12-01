import uuid

import pytest

from app.models import Asset, AuditLog, User
from app.models.auth import Project

# Mock User
MOCK_USER_ID = "test-user-id"
MOCK_USER_EMAIL = "audit@test.com"


def mock_get_current_active_user():
    return User(id=MOCK_USER_ID, email=MOCK_USER_EMAIL, is_active=True)


@pytest.fixture
def test_audit_project(db_session):
    """Create test project for audit tests"""
    from app.models.auth import Client

    # Create mock user in database (needed for foreign key in audit_logs)
    mock_user = db_session.query(User).filter(User.id == MOCK_USER_ID).first()
    if not mock_user:
        mock_user = User(
            id=MOCK_USER_ID, email=MOCK_USER_EMAIL, hashed_password="test", is_active=True
        )
        db_session.add(mock_user)
        db_session.flush()

    # Check if client exists, create if not
    client = db_session.query(Client).filter(Client.id == "test-client-audit").first()
    if not client:
        client = Client(id="test-client-audit", name="Test Audit Client")
        db_session.add(client)
        db_session.flush()

    # Check if project exists, create if not
    project = db_session.query(Project).filter(Project.id == "audit-project").first()
    if not project:
        project = Project(
            id="audit-project",
            name="Test Audit Project",
            client_id="test-client-audit",
        )
        db_session.add(project)

    db_session.commit()
    return project


def test_audit_logging(client, db_session, test_audit_project):
    # Override auth for this test
    from app.api.deps import get_current_active_user
    from app.main import app

    app.dependency_overrides[get_current_active_user] = mock_get_current_active_user

    db = db_session
    # Clear DB
    db.query(AuditLog).delete()
    db.query(Asset).delete()
    db.commit()

    # Generate unique tag to avoid conflicts with parallel tests
    unique_tag = f"AUDIT-TAG-{uuid.uuid4().hex[:8]}"

    # 1. Test Create Asset Log
    response = client.post(
        "/api/v1/assets/",
        headers={"X-Project-ID": "audit-project"},
        json={
            "tag": unique_tag,
            "description": "Audit Test Asset",
            "type": "MOTOR",
            "electrical": {"voltage": "480V"},
        },
    )
    # API returns 201 Created for successful asset creation
    assert (
        response.status_code == 201
    ), f"Expected 201, got {response.status_code}: {response.json()}"
    asset_id = response.json()["id"]

    # Verify Log
    log = (
        db.query(AuditLog)
        .filter(AuditLog.target_id == asset_id, AuditLog.action == "CREATE")
        .first()
    )
    assert log is not None
    assert log.user_id == MOCK_USER_ID
    assert log.target_type == "ASSET"
    assert log.details["tag"] == unique_tag

    print("✅ test_audit_logging (Create) passed")

    # 2. Test Update Asset Log
    response = client.put(
        f"/api/v1/assets/{asset_id}",
        headers={"X-Project-ID": "audit-project"},
        json={"description": "Updated Description"},
    )
    assert response.status_code == 200

    # Verify Log
    log = (
        db.query(AuditLog)
        .filter(AuditLog.target_id == asset_id, AuditLog.action == "UPDATE")
        .order_by(AuditLog.timestamp.desc())
        .first()
    )
    assert log is not None
    assert log.details["changes"]["description"] == "Updated Description"

    print("✅ test_audit_logging (Update) passed")
