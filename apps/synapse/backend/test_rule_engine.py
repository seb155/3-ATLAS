from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.database import Base, engine
from app.main import app
from app.models.metamodel import MetamodelEdge, MetamodelNode

# Create tables for test
Base.metadata.create_all(bind=engine)

client = TestClient(app)

def clear_db():
    with Session(engine) as session:
        session.query(MetamodelEdge).delete()
        session.query(MetamodelNode).delete()
        session.commit()

def test_rule_engine_smart_matching():
    clear_db()
    # 1. Seed Initial Data (Simulate existing assets)
    # Create a Pump and a Motor that SHOULD be linked
    # PU-100 and MO-100

    # Note: We need to use the API or DB directly. Using API for simplicity if possible,
    # but direct DB access in test is often easier for setup.
    # Let's use the client to seed via the metamodel API for consistency.

    # Create Pump PU-100
    client.post("/api/v1/metamodel/node", json={
        "name": "PU-100", "type": "PUMP", "discipline": "PROCESS", "semantic_type": "ASSET", "lod": 2
    })

    # Create Motor MO-100 (The match)
    client.post("/api/v1/metamodel/node", json={
        "name": "MO-100", "type": "MOTOR", "discipline": "ELECTRICAL", "semantic_type": "ASSET", "lod": 2
    })

    # Create Pump PU-200 (No match, should create MO-200)
    client.post("/api/v1/metamodel/node", json={
        "name": "PU-200", "type": "PUMP", "discipline": "PROCESS", "semantic_type": "ASSET", "lod": 2
    })

    # 2. Run Import (which triggers Rule Engine)
    # We use the mock import endpoint, but we need to make sure it doesn't wipe our manual seed if we want to test matching.
    # Actually, the import-mock endpoint loads from JSON.
    # To test the Rule Engine logic specifically, we might want to call the engine directly or use a test-specific endpoint.
    # However, the plan says "Import Mock Data" triggers it.
    # Let's rely on the fact that the Rule Engine scans ALL assets in the DB.
    # So if we call import, it will load the JSON *AND* process our manually created PU-100/PU-200 if they are in the DB.
    # But wait, import might duplicate if we are not careful.
    # Let's just call the rule engine via a helper or assume the import adds to the DB.

    # Let's use the import endpoint. It loads Gold Mine data.
    # Gold Mine has 310-PP-001.
    # Let's Pre-Seed 310-M-001 to test if it links instead of creating 310-PP-001-MO.

    # Pre-seed matching motor for Gold Mine asset
    res = client.post("/api/v1/metamodel/node", json={
        "name": "310-M-001", "type": "MOTOR", "discipline": "ELECTRICAL", "semantic_type": "ASSET", "lod": 2, "description": "Existing Match"
    })
    assert res.status_code == 200, f"Failed to create 310-M-001: {res.text}"

    response = client.post("/api/v1/mock/import-gold-mine")
    assert response.status_code == 200
    logs = response.json()["logs"]

    # Debug: Print all logs
    print("\n--- SYSTEM LOGS ---")
    for l in logs:
        print(f"[{l['level']}] {l['message']}")
    print("-------------------")

    # 3. Verify Logs
    # Should see LINK for 310-PP-001 -> 310-M-001
    # Should see CREATE for others

    link_log = next((l for l in logs if "LINK" in l["level"] and "310-M-001" in l["message"]), None)
    assert link_log is not None, "Should have linked to existing 310-M-001"

    create_log = next((l for l in logs if "CREATE" in l["level"] and "420-PP-001" in l["message"]), None)
    assert create_log is not None, "Should have created motor for 420-PP-001"

def test_rule_engine_idempotency():
    # Run import twice
    client.post("/api/v1/mock/import-gold-mine")
    response = client.post("/api/v1/mock/import-gold-mine")

    assert response.status_code == 200
    logs = response.json()["logs"]

    # Should see SKIP for everything
    skip_log = next((l for l in logs if "SKIP" in l["level"]), None)
    assert skip_log is not None, "Should skip existing links on second run"
