import os
import sys
import uuid

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path
# We are in /app/tests/manual, we need /app in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.models.auth import Client, Project
from app.models.metamodel import MetamodelEdge
from app.models.models import Asset
from app.models.rules import RuleActionType, RuleDefinition, RuleSource
from app.services.rule_executor import RuleExecutor

# Setup DB
# When running inside docker-compose.dev.yml, the DB host is forge-postgres
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@forge-postgres:5432/synapse"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def test_create_relationship():
    print("🧪 Starting Test: CREATE_RELATIONSHIP")

    # 1. Setup Client & Project
    client_id = "test-client"
    # Check if client exists or create
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        client = Client(id=client_id, name="Test Client", contact_email="test@example.com")
        db.add(client)
        db.commit()
        print(f"✅ Created Client: {client_id}")

    project_id = f"test-proj-{uuid.uuid4().hex[:8]}"
    project = Project(id=project_id, name="Test Project", client_id=client_id, country="US")
    db.add(project)
    db.commit()
    print(f"✅ Created Project: {project_id}")

    # 2. Create Assets (Pump and Motor)
    pump = Asset(
        tag="P-101",
        type="PUMP",
        project_id=project_id,
        properties={"area": "100"}
    )
    motor = Asset(
        tag="M-101",
        type="MOTOR",
        project_id=project_id,
        properties={"area": "100"}
    )
    db.add(pump)
    db.add(motor)
    db.commit()
    print("✅ Created Assets: P-101, M-101")

    # 3. Create Rule
    rule = RuleDefinition(
        name="Link Pump to Motor",
        source=RuleSource.PROJECT,
        action_type=RuleActionType.CREATE_RELATIONSHIP,
        condition={"asset_type": "PUMP"},
        action={
            "create_relationship": {
                "relation": "powered_by",
                "target_tag": "M-101", # Hardcoded for this test, usually {tag}-M
                "direction": "outgoing" # Pump -> Motor
            }
        },
        source_id=project_id
    )
    db.add(rule)
    db.commit()
    print("✅ Created Rule: Link Pump to Motor")

    # 4. Execute Rule
    executor = RuleExecutor(db, project_id)
    execution = executor.execute_rule(rule, pump)

    print(f"⚡ Rule Executed. Action: {execution.action_type}")
    print(f"   Details: {execution.action_taken}")

    # 5. Verify Edge
    edge = db.query(MetamodelEdge).filter(
        MetamodelEdge.source_node_id == pump.id,
        MetamodelEdge.target_node_id == motor.id,
        MetamodelEdge.relation_type == "powered_by"
    ).first()

    if edge:
        print("✅ SUCCESS: Edge created (P-101 -> M-101)")
    else:
        print("❌ FAILURE: Edge NOT found")

    # Cleanup
    # db.delete(edge)
    # db.delete(rule)
    # db.delete(pump)
    # db.delete(motor)
    # db.delete(project)
    # db.commit()

if __name__ == "__main__":
    try:
        test_create_relationship()
    except Exception as e:
        print(f"❌ ERROR: {e}")
    finally:
        db.close()
