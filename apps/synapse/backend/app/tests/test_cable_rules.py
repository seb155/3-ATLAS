import uuid

from app.core.database import SessionLocal
from app.models.cables import Cable
from app.models.models import Asset
from app.models.rules import RuleDefinition
from app.services.rule_executor import RuleExecutor


def test_cable_creation_rule():
    db = SessionLocal()
    try:
        # 1. Create Client and Project
        from app.models.auth import Client, Project

        client = Client(name=f"Test Client {uuid.uuid4()}")
        db.add(client)
        db.commit()

        project = Project(name=f"Test Project {uuid.uuid4()}", client_id=client.id, status="ACTIVE")
        db.add(project)
        db.commit()
        project_id = project.id

        # 2. Create a Motor
        motor = Asset(
            tag=f"TEST-MOTOR-{uuid.uuid4().hex[:8]}",
            type="MOTOR",
            project_id=project_id,
            properties={"hp": 100.0},
        )
        db.add(motor)
        db.commit()

        # 3. Get the Rule
        rule = (
            db.query(RuleDefinition)
            .filter(RuleDefinition.name == "FIRM: Create Power Cable for Motors")
            .first()
        )

        assert rule is not None, "Rule not found. Did you seed it?"

        # 4. Execute Rule
        executor = RuleExecutor(db, str(project_id))
        result = executor.execute_rule(rule, motor)

        print(f"Execution Result: {result.action_taken}")

        # 5. Verify Cable Created
        cable = db.query(Cable).filter(Cable.project_id == project_id).first()
        assert cable is not None
        assert cable.tag == f"{motor.tag}-PWR"
        assert cable.conductor_size is not None
        assert cable.voltage_drop_percent is not None

        print(
            f"Created Cable: {cable.tag}, "
            f"Size: {cable.conductor_size}, "
            f"VD: {cable.voltage_drop_percent}%"
        )

    finally:
        db.close()


if __name__ == "__main__":
    test_cable_creation_rule()
