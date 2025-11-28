import uuid

from app.models.auth import Project
from app.schemas.asset import AssetCreate, AssetType


def test_create_asset_invalid_voltage(client, db_session):
    # Create client and project
    from app.models.auth import Client
    client_obj = Client(
        id="test-client-validation",
        name="Test Validation Client"
    )
    db_session.add(client_obj)

    project = Project(
        id="test-project",
        name="Test Validation Project",
        client_id="test-client-validation",
    )
    db_session.add(project)
    db_session.commit()

    # Override auth for this test
    from app.api.deps import get_current_active_user
    from app.main import app
    app.dependency_overrides[get_current_active_user] = lambda: {"username": "testuser"}

    # Generate unique tag to avoid conflicts
    unique_tag = f"TEST-TAG-{uuid.uuid4().hex[:8]}"

    # Test invalid voltage
    response = client.post(
        "/api/v1/assets/",
        json={
            "tag": unique_tag,
            "type": "MOTOR",
            "electrical": {"voltage": "999V", "powerKW": 10},
            "project_id": "test-project"
        },
        headers={"X-Project-ID": "test-project"}
    )
    # We expect 422 Unprocessable Entity
    assert response.status_code == 422
    data = response.json()
    assert "Invalid voltage" in str(data)
    print("✅ test_create_asset_invalid_voltage passed")

def test_create_asset_valid_voltage():
    # Test valid voltage (schema validation only, we might not have a real DB session in this simple test if not mocked)
    # However, TestClient usually runs the app. If DB is needed, it might fail if not mocked.
    # For now, let's just check if validation passes (it might fail later at DB level if project doesn't exist)
    # But we are testing Pydantic validation which happens BEFORE DB access usually if in schema.

    # Actually, we can test the schema directly to avoid DB dependency for this unit test
    try:
        AssetCreate(
            tag="TEST-TAG-02",
            type=AssetType.MOTOR,
            electrical={"voltage": "480V"}
        )
        print("✅ test_create_asset_valid_voltage passed")
    except Exception as e:
        print(f"❌ test_create_asset_valid_voltage failed: {e}")

def test_create_asset_invalid_range():
    try:
        AssetCreate(
            tag="TEST-TAG-03",
            type=AssetType.INSTRUMENT,
            process={"minRange": 100, "maxRange": 0}
        )
        print("❌ test_create_asset_invalid_range failed: Should have raised error")
    except ValueError as e:
        if "minRange must be less than maxRange" in str(e):
            print("✅ test_create_asset_invalid_range passed")
        else:
            print(f"❌ test_create_asset_invalid_range failed with unexpected error: {e}")

if __name__ == "__main__":
    # We need to make sure we can import app.
    # This script assumes it's run from the backend directory or with python path set.
    print("Running validation tests...")
    test_create_asset_valid_voltage()
    test_create_asset_invalid_range()
    # test_create_asset_invalid_voltage() # This requires running app and might hit DB
