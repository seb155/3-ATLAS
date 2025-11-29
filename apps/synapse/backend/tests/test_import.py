
import pytest

from app.models.auth import Project
from app.models.models import Asset, AssetType


@pytest.fixture
def test_import_project(db_session):
    """Create test project for import tests"""
    from app.models.auth import Client

    # Use get_or_create pattern to avoid constraint violations
    client = db_session.query(Client).filter(Client.id == "test-client-import").first()
    if not client:
        client = Client(
            id="test-client-import",
            name="Test Import Client"
        )
        db_session.add(client)
        db_session.flush()

    project = db_session.query(Project).filter(Project.id == "test-project-import").first()
    if not project:
        project = Project(
            id="test-project-import",
            name="Test Import Project",
            client_id="test-client-import",
        )
        db_session.add(project)
        db_session.commit()

    return project

def test_import_csv(client, db_session, test_import_project):
    # Override auth for this test
    from app.api.deps import get_current_active_user
    from app.main import app
    app.dependency_overrides[get_current_active_user] = lambda: {"username": "testuser"}

    db = db_session
    db.query(Asset).delete()
    db.commit()

    # 1. Prepare CSV Content
    # Row 1: New Asset (Valid)
    # Row 2: Invalid Asset (Missing Type)
    csv_content = """tag,description,type,electrical.voltage,process.fluid
IMPORT-NEW-01,New Asset Description,MOTOR,480V,Water
IMPORT-INVALID-01,Invalid Asset Description,,480V,Air
"""

    # 2. Send Request
    files = {"file": ("test.csv", csv_content, "text/csv")}
    response = client.post(
        "/api/v1/import_export/import",
        headers={"X-Project-ID": "test-project-import"},
        files=files
    )

    if response.status_code != 200:
        print(f"❌ Request failed: {response.status_code}")
        print(response.text)

    assert response.status_code == 200
    data = response.json()

    print(f"Response: {data}")

    # 3. Verify Response Summary
    assert data["created"] == 1
    assert len(data["errors"]) == 1
    assert "type" in str(data["errors"][0]).lower()

    # 4. Verify DB
    asset = db.query(Asset).filter(Asset.tag == "IMPORT-NEW-01").first()
    assert asset is not None
    assert asset.description == "New Asset Description"
    assert asset.electrical["voltage"] == "480V"

    print("✅ test_import_csv (Create) passed")

def test_import_update_csv(client, db_session, test_import_project):
    # Override auth for this test
    from app.api.deps import get_current_active_user
    from app.main import app
    app.dependency_overrides[get_current_active_user] = lambda: {"username": "testuser"}

    # 1. Create existing asset
    db = db_session
    asset = Asset(
        tag="IMPORT-UPDATE-01",
        description="Original Description",
        type=AssetType.MOTOR,
        project_id="test-project-import",
        electrical={"voltage": "120V"}
    )
    db.add(asset)
    db.commit()

    # 2. Prepare CSV to update it
    csv_content = """tag,description,electrical.voltage
IMPORT-UPDATE-01,Updated Description,480V
"""

    files = {"file": ("update.csv", csv_content, "text/csv")}
    response = client.post(
        "/api/v1/import_export/import",
        headers={"X-Project-ID": "test-project-import"},
        files=files
    )

    assert response.status_code == 200
    data = response.json()

    assert data["updated"] == 1
    assert data["created"] == 0

    # 3. Verify DB
    asset = db.query(Asset).filter(Asset.tag == "IMPORT-UPDATE-01").first()
    assert asset.description == "Updated Description"
    assert asset.electrical["voltage"] == "480V"

    print("✅ test_import_update_csv passed")
