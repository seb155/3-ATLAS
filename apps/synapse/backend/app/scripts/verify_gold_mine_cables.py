import logging

from app.core.database import SessionLocal
from app.models.auth import Project
from app.models.models import Asset
from app.models.rules import RuleActionType, RuleDefinition, RuleSource
from app.services.metamodel import MetamodelService
from app.services.rule_executor import RuleExecutor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def verify_gold_mine_cables():
    db = SessionLocal()
    try:
        logger.info("Starting Gold Mine Cable Verification...")

        # 1. Get Project
        project_id = "project-gold-mine-001"
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            logger.error(f"Project {project_id} not found!")
            return

        # 2. Get Motors
        motors = db.query(Asset).filter(Asset.project_id == project_id, Asset.type == "MOTOR").all()

        if not motors:
            logger.warning("No motors found in Gold Mine project. Creating a test motor...")
            # Create a test motor if none exist
            motor = Asset(
                tag="310-PP-001-M",
                type="MOTOR",
                project_id=project_id,
                area="310",
                system="GRINDING",
                properties={"hp": 100, "voltage": "600V"},
            )
            db.add(motor)
            db.commit()
            db.refresh(motor)

            # Create Metamodel Node
            MetamodelService.create_node_from_asset(db, motor)
            motors = [motor]

        logger.info(f"Found {len(motors)} motors to process.")

        # 3. Create/Get Rule
        rule_name = "FIRM: Create Power Cable for Motors"
        rule = (
            db.query(RuleDefinition)
            .filter(RuleDefinition.name == rule_name, RuleDefinition.source == RuleSource.FIRM)
            .first()
        )

        if not rule:
            logger.info("Creating FIRM rule for cable generation...")
            rule = RuleDefinition(
                name=rule_name,
                description="Automatically create power cables for all motors",
                source=RuleSource.FIRM,
                priority=10,
                discipline="ELECTRICAL",
                category="CABLE",
                action_type=RuleActionType.CREATE_CABLE,
                is_active=True,
                condition={"asset_type": "MOTOR"},
                action={
                    "create_cable": {
                        "cable_tag": "{tag}-PWR",
                        "cable_type": "3C+G",
                        "sizing_method": "Auto",
                        "length_meters": 50,  # Default length
                        "voltage": "600V",
                    }
                },
            )
            db.add(rule)
            db.commit()
            db.refresh(rule)

        # 4. Execute Rule
        executor = RuleExecutor(db, project_id)
        logger.info(f"Executing rule '{rule.name}' on {len(motors)} motors...")

        actions_taken = 0
        for motor in motors:
            result = executor.execute_rule(rule, motor)
            if result.action_type != "SKIP":
                actions_taken += 1

        logger.info(f"Execution Complete. Actions taken: {actions_taken}")

        # 5. Verify Cables
        cables = db.query(Asset).filter(Asset.project_id == project_id, Asset.type == "CABLE").all()

        logger.info(f"Total Cables in Project: {len(cables)}")

        for cable in cables:
            props = cable.properties
            logger.info(
                f"Cable {cable.tag}: Size={props.get('cable_size')}, "
                f"VD={props.get('voltage_drop_percent')}%"
            )

            if not props.get("cable_size"):
                logger.error(f"❌ Cable {cable.tag} missing sizing!")
            else:
                logger.info(f"✅ Cable {cable.tag} verified.")

    except Exception as e:
        logger.error(f"Verification Failed: {e}")
        import traceback

        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    verify_gold_mine_cables()
