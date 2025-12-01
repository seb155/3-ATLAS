"""
Tests for Rule Engine (Database-Driven Rules)

Tests all components:
- RuleDefinition model
- RuleLoader service
- RuleExecutor service
- RuleEngine integration
- Rule API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.auth import Project
from app.models.models import Asset
from app.models.rules import RuleActionType, RuleDefinition, RuleExecution, RuleSource
from app.services.rule_engine import RuleEngine
from app.services.rule_executor import RuleExecutor
from app.services.rule_loader import RuleLoader

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def test_project(db_session: Session):
    """Create test project"""
    from app.models.auth import Client

    # Check if client exists, create if not
    client = db_session.query(Client).filter(Client.id == "test-client").first()
    if not client:
        client = Client(id="test-client", name="Test Client")
        db_session.add(client)
        db_session.flush()

    # Check if project exists, create if not
    project = db_session.query(Project).filter(Project.id == "test-project-123").first()
    if not project:
        project = Project(
            id="test-project-123",
            name="Test Project",
            client_id="test-client",
            country="CA",  # For COUNTRY-level rule testing
        )
        db_session.add(project)

    db_session.commit()
    return project


@pytest.fixture
def firm_rule(db_session: Session):
    """Create FIRM-level test rule"""
    rule = RuleDefinition(
        name="Test FIRM Rule: Pump → Motor",
        source=RuleSource.FIRM,
        priority=10,
        discipline="ELECTRICAL",
        action_type=RuleActionType.CREATE_CHILD,
        condition={"asset_type": "PUMP"},
        action={
            "create_child": {
                "type": "MOTOR",
                "naming": "{parent_tag}-M",
                "relation": "powers",
                "discipline": "ELECTRICAL",
                "semantic_type": "ASSET",
                "properties": {"motor_type": "Electric"},
            }
        },
        is_active=True,
    )
    db_session.add(rule)
    db_session.commit()
    db_session.refresh(rule)
    return rule


@pytest.fixture
def country_rule(db_session: Session):
    """Create COUNTRY-level test rule (higher priority)"""
    rule = RuleDefinition(
        name="Test COUNTRY-CA Rule: Set 600V",
        source=RuleSource.COUNTRY,
        source_id="CA",
        priority=30,
        discipline="ELECTRICAL",
        action_type=RuleActionType.SET_PROPERTY,
        condition={"asset_type": "MOTOR"},
        action={
            "set_property": {
                "voltage": "600V",
                "frequency": "60Hz",
            }
        },
        is_active=True,
    )
    db_session.add(rule)
    db_session.commit()
    db_session.refresh(rule)
    return rule


@pytest.fixture
def test_pump(db_session: Session, test_project):
    """Create test pump asset"""
    pump = Asset(
        tag="310-PP-001",
        type="PUMP",
        semantic_type="ASSET",
        project_id=test_project.id,
        properties={"pump_type": "CENTRIFUGAL", "area": "310"},
    )
    db_session.add(pump)
    db_session.commit()
    db_session.refresh(pump)
    return pump


# ============================================================================
# RuleLoader Tests
# ============================================================================


def test_rule_loader_loads_firm_rules(db_session: Session, test_project, firm_rule):
    """Test RuleLoader loads FIRM rules"""
    rules = RuleLoader.load_rules_for_project(db_session, test_project.id)

    assert len(rules) >= 1
    assert firm_rule.id in [r.id for r in rules]
    assert all(r.is_active for r in rules)


def test_rule_loader_loads_country_rules(db_session: Session, test_project, country_rule):
    """Test RuleLoader loads COUNTRY rules for project country"""
    rules = RuleLoader.load_rules_for_project(db_session, test_project.id)

    # Should include country rule for CA
    assert country_rule.id in [r.id for r in rules]


def test_rule_loader_priority_order(db_session: Session, test_project, firm_rule, country_rule):
    """Test RuleLoader sorts by priority (highest first)"""
    rules = RuleLoader.load_rules_for_project(db_session, test_project.id)

    # Country rule (priority 30) should come before FIRM rule (priority 10)
    priorities = [r.priority for r in rules]
    assert priorities == sorted(priorities, reverse=True)


def test_rule_loader_excludes_inactive(db_session: Session, test_project, firm_rule):
    """Test RuleLoader excludes inactive rules"""
    firm_rule.is_active = False
    db_session.commit()

    rules = RuleLoader.load_rules_for_project(db_session, test_project.id)

    assert firm_rule.id not in [r.id for r in rules]


# ============================================================================
# RuleExecutor Tests
# ============================================================================


def test_executor_evaluates_condition_match(
    db_session: Session, test_project, firm_rule, test_pump
):
    """Test RuleExecutor evaluates matching condition"""
    executor = RuleExecutor(db_session, test_project.id)

    matched = executor._evaluate_condition(firm_rule.condition, test_pump)

    assert matched is True


def test_executor_evaluates_condition_no_match(db_session: Session, test_project, firm_rule):
    """Test RuleExecutor evaluates non-matching condition"""
    executor = RuleExecutor(db_session, test_project.id)

    # Create TANK (should not match PUMP rule)
    tank = Asset(
        tag="310-TK-001",
        type="TANK",
        semantic_type="ASSET",
        project_id=test_project.id,
    )

    matched = executor._evaluate_condition(firm_rule.condition, tank)

    assert matched is False


def test_executor_creates_child(db_session: Session, test_project, firm_rule, test_pump):
    """Test RuleExecutor creates child asset"""
    executor = RuleExecutor(db_session, test_project.id)

    # Execute rule
    execution = executor.execute_rule(firm_rule, test_pump)

    # Verify execution log
    assert execution.action_type == "CREATE"
    assert execution.condition_matched is True
    assert execution.created_entity_type == "MOTOR"
    assert "310-PP-001-M" in execution.action_taken

    # Verify child was created (RuleExecutor creates Asset, not MetamodelNode)
    motor = (
        db_session.query(Asset)
        .filter(Asset.tag == "310-PP-001-M", Asset.project_id == test_project.id)
        .first()
    )
    assert motor is not None
    assert motor.type == "MOTOR"


def test_executor_idempotency(db_session: Session, test_project, firm_rule, test_pump):
    """Test RuleExecutor doesn't create duplicates"""
    executor = RuleExecutor(db_session, test_project.id)

    # Execute rule twice
    execution1 = executor.execute_rule(firm_rule, test_pump)
    execution2 = executor.execute_rule(firm_rule, test_pump)

    # First should create, second should skip
    assert execution1.action_type == "CREATE"
    assert execution2.action_type == "SKIP"

    # Verify only one motor exists
    motors = db_session.query(Asset).filter(Asset.tag == "310-PP-001-M").all()
    assert len(motors) == 1


def test_executor_set_property(db_session: Session, test_project, country_rule):
    """Test RuleExecutor sets properties"""
    executor = RuleExecutor(db_session, test_project.id)

    # Create motor
    motor = Asset(
        tag="310-PP-001-M",
        type="MOTOR",
        semantic_type="ASSET",
        project_id=test_project.id,
        properties={},
    )
    db_session.add(motor)
    db_session.commit()

    # Execute rule
    execution = executor.execute_rule(country_rule, motor)

    # Verify execution
    assert execution.action_type == "UPDATE"
    assert execution.condition_matched is True

    # Verify properties were set
    db_session.refresh(motor)
    assert motor.properties["voltage"] == "600V"
    assert motor.properties["frequency"] == "60Hz"


def test_executor_property_filters(db_session: Session, test_project):
    """Test RuleExecutor evaluates property filters"""
    # Create rule with property filter
    rule = RuleDefinition(
        name="Test Property Filter",
        source=RuleSource.FIRM,
        priority=10,
        action_type=RuleActionType.SET_PROPERTY,
        condition={
            "asset_type": "PUMP",
            "property_filters": [{"key": "pump_type", "op": "==", "value": "CENTRIFUGAL"}],
        },
        action={"set_property": {"manufacturer": "Flowserve"}},
        is_active=True,
    )
    db_session.add(rule)
    db_session.commit()

    executor = RuleExecutor(db_session, test_project.id)

    # Test matching asset
    pump1 = Asset(
        tag="PUMP-1",
        type="PUMP",
        properties={"pump_type": "CENTRIFUGAL"},
        project_id=test_project.id,
    )
    assert executor._evaluate_condition(rule.condition, pump1) is True

    # Test non-matching asset
    pump2 = Asset(
        tag="PUMP-2",
        type="PUMP",
        properties={"pump_type": "POSITIVE_DISPLACEMENT"},
        project_id=test_project.id,
    )
    assert executor._evaluate_condition(rule.condition, pump2) is False


def test_executor_operators(db_session: Session, test_project):
    """Test RuleExecutor operator evaluation"""
    executor = RuleExecutor(db_session, test_project.id)

    # Test ==
    assert executor._evaluate_operator("PUMP", "==", "PUMP") is True
    assert executor._evaluate_operator("PUMP", "==", "TANK") is False

    # Test !=
    assert executor._evaluate_operator("PUMP", "!=", "TANK") is True

    # Test >
    assert executor._evaluate_operator(100, ">", 50) is True
    assert executor._evaluate_operator(50, ">", 100) is False

    # Test in
    assert executor._evaluate_operator("PUMP", "in", ["PUMP", "TANK"]) is True
    assert executor._evaluate_operator("VALVE", "in", ["PUMP", "TANK"]) is False

    # Test contains
    assert executor._evaluate_operator("CENTRIFUGAL", "contains", "CENTR") is True


# ============================================================================
# RuleEngine Integration Tests
# ============================================================================


def test_rule_engine_applies_rules(db_session: Session, test_project, firm_rule, test_pump):
    """Test RuleEngine applies all rules to all assets"""
    # Execute rule engine
    summary = RuleEngine.apply_rules(db_session, test_project.id)

    # Verify summary
    assert summary["total_rules"] >= 1
    assert summary["total_assets"] >= 1
    assert summary["total_executions"] >= 1
    assert summary["actions_taken"] >= 1

    # Verify motor was created
    motor = db_session.query(Asset).filter(Asset.tag == "310-PP-001-M").first()
    assert motor is not None


def test_rule_engine_priority_override(db_session: Session, test_project, firm_rule, country_rule):
    """Test higher priority rules override lower priority"""
    # Create motor
    motor = Asset(
        tag="TEST-MOTOR",
        type="MOTOR",
        semantic_type="ASSET",
        project_id=test_project.id,
        properties={},
    )
    db_session.add(motor)
    db_session.commit()

    # Execute rule engine
    RuleEngine.apply_rules(db_session, test_project.id)

    # Verify COUNTRY rule (priority 30) was applied
    db_session.refresh(motor)
    assert motor.properties["voltage"] == "600V"  # From country rule


def test_rule_engine_execution_logs(db_session: Session, test_project, firm_rule, test_pump):
    """Test RuleEngine creates execution logs"""
    # Execute rule engine
    RuleEngine.apply_rules(db_session, test_project.id)

    # Verify execution logs exist
    executions = (
        db_session.query(RuleExecution).filter(RuleExecution.project_id == test_project.id).all()
    )

    assert len(executions) >= 1

    # Verify log details
    execution = executions[0]
    assert execution.rule_id == firm_rule.id
    assert execution.asset_id == test_pump.id
    assert execution.execution_time_ms is not None


def test_rule_engine_error_handling(db_session: Session, test_project, test_pump):
    """Test RuleEngine handles errors gracefully"""
    # Create invalid rule (missing required action field)
    bad_rule = RuleDefinition(
        name="Bad Rule",
        source=RuleSource.FIRM,
        priority=10,
        action_type=RuleActionType.CREATE_CHILD,
        condition={"asset_type": "PUMP"},
        action={},  # Missing create_child
        is_active=True,
    )
    db_session.add(bad_rule)
    db_session.commit()

    # Execute should not crash
    summary = RuleEngine.apply_rules(db_session, test_project.id)

    # Should log errors
    assert summary["errors"] >= 1


# ============================================================================
# API Endpoint Tests
# ============================================================================


def test_api_list_rules(client: TestClient, db_session: Session, firm_rule):
    """Test GET /api/v1/rules"""
    response = client.get("/api/v1/rules")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert len(data["rules"]) >= 1


def test_api_create_rule(client: TestClient, db_session: Session):
    """Test POST /api/v1/rules"""
    import uuid

    unique_name = f"API Test Rule {uuid.uuid4().hex[:8]}"
    rule_data = {
        "name": unique_name,
        "source": "FIRM",
        "discipline": "ELECTRICAL",
        "action_type": "CREATE_CHILD",
        "condition": {"asset_type": "VALVE"},
        "action": {
            "create_child": {
                "type": "ACTUATOR",
                "naming": "{parent_tag}-ACT",
                "relation": "actuated_by",
            }
        },
        "is_active": True,
    }

    response = client.post("/api/v1/rules", json=rule_data)

    if response.status_code != 201:
        print(f"DEBUG: Create rule failed with {response.status_code}: {response.json()}")
    assert (
        response.status_code == 201
    ), f"Expected 201, got {response.status_code}: {response.json()}"
    data = response.json()
    assert data["name"] == unique_name
    assert data["priority"] == 10  # Auto-assigned for FIRM


def test_api_update_rule(client: TestClient, db_session: Session, firm_rule):
    """Test PUT /api/v1/rules/{rule_id}"""
    update_data = {
        "name": "Updated Rule Name",
        "is_active": False,
    }

    response = client.put(f"/api/v1/rules/{firm_rule.id}", json=update_data)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Rule Name"
    assert data["is_active"] is False
    assert data["version"] == 2  # Version incremented


def test_api_delete_rule(client: TestClient, db_session: Session, firm_rule):
    """Test DELETE /api/v1/rules/{rule_id}"""
    response = client.delete(f"/api/v1/rules/{firm_rule.id}")

    assert response.status_code == 204

    # Verify deleted
    deleted = db_session.query(RuleDefinition).filter(RuleDefinition.id == firm_rule.id).first()
    assert deleted is None


def test_api_test_rule(client: TestClient, db_session: Session, firm_rule):
    """Test POST /api/v1/rules/{rule_id}/test"""
    test_data = {
        "sample_assets": [
            {"tag": "TEST-PP-001", "type": "PUMP"},
            {"tag": "TEST-TK-001", "type": "TANK"},
        ]
    }

    response = client.post(f"/api/v1/rules/{firm_rule.id}/test", json=test_data)

    assert response.status_code == 200
    data = response.json()
    assert data["rule_id"] == firm_rule.id
    assert len(data["test_results"]) == 2

    # Pump should match
    assert data["test_results"][0]["condition_matched"] is True
    assert "MOTOR" in data["test_results"][0]["would_create"]

    # Tank should not match
    assert data["test_results"][1]["condition_matched"] is False


def test_api_execution_logs(
    client: TestClient, db_session: Session, test_project, firm_rule, test_pump
):
    """Test GET /api/v1/rules/executions/logs"""
    # Execute rule to create logs
    executor = RuleExecutor(db_session, test_project.id)
    executor.execute_rule(firm_rule, test_pump)

    response = client.get(f"/api/v1/rules/executions/logs?project_id={test_project.id}")

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["rule_id"] == firm_rule.id


def test_api_execution_summary(
    client: TestClient, db_session: Session, test_project, firm_rule, test_pump
):
    """Test GET /api/v1/rules/executions/summary"""
    # Execute rule
    RuleEngine.apply_rules(db_session, test_project.id)

    response = client.get(f"/api/v1/rules/executions/summary?project_id={test_project.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["total_executions"] >= 1
    assert data["total_rules"] >= 1
    assert data["time_elapsed_ms"] >= 0


# ============================================================================
# Stats and Performance Tests
# ============================================================================


def test_rule_stats_updated(db_session: Session, test_project, firm_rule, test_pump):
    """Test rule statistics are updated on execution"""
    initial_count = firm_rule.execution_count
    initial_success = firm_rule.success_count

    # Execute rule
    executor = RuleExecutor(db_session, test_project.id)
    executor.execute_rule(firm_rule, test_pump)

    db_session.refresh(firm_rule)

    assert firm_rule.execution_count == initial_count + 1
    assert firm_rule.success_count == initial_success + 1
    assert firm_rule.last_executed_at is not None


def test_performance_many_rules_many_assets(db_session: Session, test_project):
    """Test performance with multiple rules and assets"""
    import time

    # Create 10 assets
    for i in range(10):
        asset = Asset(
            tag=f"PUMP-{i:03d}",
            type="PUMP",
            semantic_type="ASSET",
            project_id=test_project.id,
        )
        db_session.add(asset)

    # Create 5 rules
    for i in range(5):
        rule = RuleDefinition(
            name=f"Test Rule {i}",
            source=RuleSource.FIRM,
            priority=10 + i,
            action_type=RuleActionType.SET_PROPERTY,
            condition={"asset_type": "PUMP"},
            action={"set_property": {f"prop_{i}": f"value_{i}"}},
            is_active=True,
        )
        db_session.add(rule)

    db_session.commit()

    # Execute rule engine
    start = time.time()
    summary = RuleEngine.apply_rules(db_session, test_project.id)
    elapsed = time.time() - start

    # Should complete in reasonable time (< 5 seconds for 50 executions)
    assert elapsed < 5.0
    assert summary["total_executions"] == 50  # 10 assets × 5 rules
