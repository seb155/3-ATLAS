import logging
import time

from app.core.database import SessionLocal
from app.models.auth import Project
from app.models.models import Asset
from app.models.rules import RuleDefinition
from app.services.rule_executor import RuleExecutor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_integration():
    db = SessionLocal()
    try:
        logger.info("Starting Integration Test...")

        # 0. Check Client & Project
        from app.models.auth import Client

        client_id = "client-aurumax-corp"
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            logger.info(f"Client {client_id} not found. Creating...")
            client = Client(id=client_id, name="AuruMax Corp")
            db.add(client)
            db.commit()

        project_id = "project-gold-mine-001"
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            logger.info(f"Project {project_id} not found. Creating...")
            project = Project(
                id=project_id, name="Gold Mine", client_id=client_id, description="Test Project"
            )
            db.add(project)
            db.commit()

        # 1. Setup Data
        import uuid

        unique_id = str(uuid.uuid4())[:8]
        motor_tag = f"TEST-MOTOR-{unique_id}"
        motor = Asset(
            tag=motor_tag,
            type="MOTOR",
            project_id=project_id,
            properties={"hp": 50, "voltage": "600V"},  # 50HP -> 52A FLC -> 65A Min -> 6 AWG
            area="310",
            system="TEST",
        )
        db.add(motor)
        db.commit()
        logger.info(f"Created Motor: {motor.tag}")

        # Create MetamodelNode for Motor
        from app.services.metamodel import MetamodelService

        MetamodelService.create_node_from_asset(db, motor)
        db.commit()

        # Create Dummy Rule
        rule = RuleDefinition(
            name="TEST: Create Cable for Motor",
            description="Test Rule",
            source="FIRM",
            priority=10,
            discipline="ELECTRICAL",
            category="CABLE",
            action_type="CREATE_CABLE",
            condition={"asset_type": "MOTOR"},
            action={
                "create_cable": {
                    "cable_tag": "{tag}-PWR",
                    "cable_type": "3C+G",
                    "sizing_method": "Auto",
                    "length_meters": 75,
                    "voltage": "600V",
                }
            },
            is_active=True,
        )
        db.add(rule)
        db.commit()
        logger.info(f"Created Rule: {rule.name}")

        # 2. Execute Rule
        executor = RuleExecutor(db, project_id)
        result = executor._execute_create_cable(rule, motor, time.time())

        logger.info(f"Execution Result: {result.action_taken}")

        # 3. Verify Cable
        cable_tag = f"{motor_tag}-PWR"
        cable = (
            db.query(Asset).filter(Asset.tag == cable_tag, Asset.project_id == project_id).first()
        )

        if cable:
            logger.info(f"✅ Cable Created: {cable.tag}")
            props = cable.properties
            logger.info(f"Properties: {props}")

            # Verification Logic
            # 50HP @ 600V -> ~52A FLC
            # Min Ampacity = 52 * 1.25 = 65A
            # Table 2: 6 AWG is 65A (75C)
            # So expected size is 6 AWG

            assert (
                props["conductor_size"] == "6 AWG"
            ), f"Expected 6 AWG, got {props.get('conductor_size')}"
            assert props["voltage_drop_percent"] < 3.0, "Voltage drop too high"
            assert props["length"] == 75

            logger.info("✅ Sizing Verification Passed")
        else:
            logger.error("❌ Cable NOT Created")

    except Exception as e:
        import traceback

        logger.error(f"Test Failed: {e}")
        traceback.print_exc()
    finally:
        # Cleanup
        try:
            if "motor" in locals():
                db.delete(motor)
            if "rule" in locals():
                db.delete(rule)
            if "cable" in locals() and cable:
                db.delete(cable)
            db.commit()
            logger.info("Cleanup Complete")
        except Exception:
            pass
        db.close()


if __name__ == "__main__":
    test_integration()
