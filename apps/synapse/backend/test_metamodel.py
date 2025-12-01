from fastapi.testclient import TestClient

from app.core.database import Base, engine
from app.main import app

# Create tables for test
Base.metadata.create_all(bind=engine)

client = TestClient(app)


def test_metamodel_advanced_flow():
    # 1. Seed Defaults (Advanced)
    response = client.post("/api/v1/metamodel/seed")
    assert response.status_code == 200

    # Get Graph to verify
    response = client.get("/api/v1/metamodel/graph")
    assert response.status_code == 200
    graph = response.json()
    nodes = graph["nodes"]
    assert len(nodes) > 10  # Should have many more nodes now

    # Check for specific nodes
    motor = next((n for n in nodes if n["name"] == "MOTOR"), None)
    assert motor is not None
    assert motor["discipline"] == "ELECTRICAL"
    assert motor["semantic_type"] == "ASSET"

    site = next((n for n in nodes if n["name"] == "SITE"), None)
    assert site["discipline"] == "PROJECT"
    assert site["lod"] == 1

    # 2. Create Advanced Edge
    # Find IDs
    mcc_id = next(n["id"] for n in nodes if n["name"] == "MCC_600V")
    motor_id = motor["id"]

    edge_data = {
        "source_node_id": mcc_id,
        "target_node_id": motor_id,
        "relation_type": "powers_custom",
        "cardinality": "1:1",
        "discipline": "ELECTRICAL",
        "properties": {"voltage": "600V", "cable": "3C#10"},
    }
    response = client.post("/api/v1/metamodel/edge", json=edge_data)
    assert response.status_code == 200
    edge = response.json()
    assert edge["discipline"] == "ELECTRICAL"
    assert edge["properties"]["voltage"] == "600V"

    # 3. Get Graph
    response = client.get("/api/v1/metamodel/graph")
    assert response.status_code == 200
    graph = response.json()

    # Verify we have edges with properties
    edges = graph["edges"]
    assert any(e["properties"].get("voltage") == "600V" for e in edges)
