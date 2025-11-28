import csv
import io

import pytest

from app.models.auth import Project
from app.models.models import Asset, AssetType


@pytest.fixture
def test_export_project(db_session):
    """Create test project for export tests"""
    from app.models.auth import Client
    # Create client first
    client = Client(
        id="test-client-export",
        name="Test Export Client"
    )
    db_session.add(client)

    project = Project(
        id="test-project-export",
        name="Test Export Project",
        client_id="test-client-export",
    )
    db_session.add(project)
    db_session.commit()
    return project

def test_export_csv(client, db_session, test_export_project):
    # 1. Create a dummy asset directly in DB
    db = db_session
    # Clear existing
    db.query(Asset).delete()

    asset = Asset(
        tag="EXPORT-TEST-01",
        description="Test Asset for Export",
        type=AssetType.MOTOR,
        project_id="test-project-export",
        electrical={"voltage": "480V", "powerKW": 55},
        process={"fluid": "Water"}
    )
    db.add(asset)
    db.commit()

    # 2. Override auth to avoid 401
    from app.api.deps import get_current_active_user
    from app.main import app
    app.dependency_overrides[get_current_active_user] = lambda: {"username": "testuser"}

    response = client.get(
        "/api/v1/import_export/export",
        headers={"X-Project-ID": "test-project-export"}
    )

    if response.status_code != 200:
        print(f"❌ Request failed: {response.status_code}")
        print(response.text)

    assert response.status_code == 200
    if "text/csv" not in response.headers["content-type"]:
        print(f"❌ Unexpected Content-Type: {response.headers['content-type']}")

    assert "text/csv" in response.headers["content-type"]

    # 3. Parse CSV
    content = response.text
    f = io.StringIO(content)
    reader = csv.DictReader(f)
    rows = list(reader)

    assert len(rows) == 1
    row = rows[0]
    assert row["tag"] == "EXPORT-TEST-01"
    assert row["electrical.voltage"] == "480V"
    assert row["process.fluid"] == "Water"

    print("✅ test_export_csv passed")
