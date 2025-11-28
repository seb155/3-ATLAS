"""
Tests for Phase 2 Rules: Relationships and Validation
"""

import pytest
from sqlalchemy.orm import Session

from app.models.auth import Client, Project
from app.models.metamodel import MetamodelEdge
from app.models.models import Asset
from app.models.rules import RuleActionType, RuleDefinition, RuleExecution, RuleSource
from app.services.rule_executor import RuleExecutor
from app.services.validation_service import ValidationService

# Use db_session from conftest.py instead of custom db fixture

@pytest.fixture
def test_client(db_session: Session):
    """Create test client"""
    # Check if client exists first to avoid unique constraint error if test re-runs without cleanup
    client = db_session.query(Client).filter(Client.name == "Test Client").first()
    if not client:
        client = Client(id="test-client", name="Test Client")
        db_session.add(client)
        db_session.commit()
    return client

@pytest.fixture
def test_project(db_session: Session, test_client):
    """Create test project"""
    # Check if project exists
    project = db_session.query(Project).filter(Project.name == "Test Project Phase 2").first()
    if not project:
        project = Project(
            id="test-project-phase2",
            name="Test Project Phase 2",
            client_id=test_client.id,
        )
        db_session.add(project)
        db_session.commit()
    return project

@pytest.fixture
def pump_asset(db_session: Session, test_project):
    """Create test pump asset"""
    pump = db_session.query(Asset).filter(Asset.tag == "310-PP-001", Asset.project_id == test_project.id).first()
    if not pump:
        pump = Asset(
            tag="310-PP-001",
            type="PUMP",
            project_id=test_project.id,
            properties={"pump_type": "CENTRIFUGAL", "area": "310"},
        )
        db_session.add(pump)
        db_session.commit()
        db_session.refresh(pump)
    return pump

@pytest.fixture
def vfd_asset(db_session: Session, test_project):
    """Create test VFD asset"""
    vfd = db_session.query(Asset).filter(Asset.tag == "310-PP-001-VFD", Asset.project_id == test_project.id).first()
    if not vfd:
        vfd = Asset(
            tag="310-PP-001-VFD",
            type="VFD",
            project_id=test_project.id,
            properties={"voltage": "600V"},
        )
        db_session.add(vfd)
        db_session.commit()
        db_session.refresh(vfd)
    return vfd

import uuid


@pytest.fixture
def relationship_rule(db_session: Session):
    """Create relationship rule"""
    rule_name = f"Link Pump to VFD {uuid.uuid4()}"

    rule = RuleDefinition(
        name=rule_name,
        source=RuleSource.PROJECT,
        priority=50,
        action_type=RuleActionType.CREATE_RELATIONSHIP,
        condition={"asset_type": "PUMP"},
        action={
            "create_relationship": {
                "target_tag": "{tag}-VFD",
                "relation": "controlled_by",
                "direction": "incoming" # VFD -> Pump
            }
        },
        is_active=True,
    )
    db_session.add(rule)
    db_session.commit()
    yield rule
    # Cleanup
    db_session.delete(rule)
    db_session.commit()

@pytest.fixture
def validate_rule(db_session: Session):
    """Create validation rule"""
    rule_name = f"Check Pump Efficiency {uuid.uuid4()}"

    rule = RuleDefinition(
        name=rule_name,
        source=RuleSource.FIRM,
        priority=10,
        action_type=RuleActionType.VALIDATE,
        condition={
            "asset_type": "PUMP",
            "property_filters": [
                 {"key": "efficiency", "op": "<", "value": 80}
            ]
        },
        action={
            "validate": {
                "severity": "WARNING",
                "message": "Pump {tag} efficiency {efficiency}% is too low"
            }
        },
        is_active=True,
    )
    db_session.add(rule)
    db_session.commit()
    yield rule
    # Cleanup
    db_session.delete(rule)
    db_session.commit()

def test_create_relationship_rule(db_session: Session, test_project, pump_asset, vfd_asset, relationship_rule):
    """Test CREATE_RELATIONSHIP action"""
    # Cleanup existing edge if any
    existing_edge = db_session.query(MetamodelEdge).filter(
        MetamodelEdge.source_node_id == vfd_asset.id,
        MetamodelEdge.target_node_id == pump_asset.id,
        MetamodelEdge.relation_type == "controlled_by"
    ).first()
    if existing_edge:
        db_session.delete(existing_edge)
        db_session.commit()

    executor = RuleExecutor(db_session,test_project.id)
    execution = executor.execute_rule(relationship_rule, pump_asset)

    if execution.action_type != "CREATE":
        print(f"\nExecution failed: {execution.action_taken}")
        print(f"Error Message: {execution.error_message}")
        print(f"Stack Trace: {execution.stack_trace}")

    assert execution.action_type == "CREATE"
    assert execution.condition_matched is True
    assert "Created relationship controlled_by" in execution.action_taken

    # Verify edge creation
    edge = db_session.query(MetamodelEdge).filter(
        MetamodelEdge.source_node_id == vfd_asset.id,
        MetamodelEdge.target_node_id == pump_asset.id,
        MetamodelEdge.relation_type == "controlled_by"
    ).first()
    assert edge is not None

def test_validate_rule_warning(db_session: Session, test_project, pump_asset, validate_rule):
    """Test VALIDATE action (Warning)"""
    from sqlalchemy.orm.attributes import flag_modified

    # Set low efficiency
    if not pump_asset.properties:
        pump_asset.properties = {}
    pump_asset.properties["efficiency"] = 75
    flag_modified(pump_asset, "properties")  # Mark JSON field as modified
    db_session.commit()
    db_session.refresh(pump_asset)

    # Verify the property was set
    assert pump_asset.properties.get("efficiency") == 75

    executor = RuleExecutor(db_session,test_project.id)
    execution = executor.execute_rule(validate_rule, pump_asset)

    if execution.action_type != "VALIDATION_WARN":
        print(f"\nExecution result: {execution.action_type}")
        print(f"Action taken: {execution.action_taken}")
        print(f"Condition matched: {execution.condition_matched}")

    assert execution.action_type == "VALIDATION_WARN"
    assert "efficiency 75% is too low" in execution.action_taken

def test_validation_service(db_session: Session, test_project, pump_asset):
    """Test ValidationService aggregation"""
    # Cleanup existing logs for this asset
    db_session.query(RuleExecution).filter(RuleExecution.asset_id == pump_asset.id).delete()
    db_session.commit()

    # Create dummy rules for the executions
    rule1 = RuleDefinition(
        id="rule-validation-1",
        name="Dummy Validation Rule 1",
        source=RuleSource.FIRM,
        priority=10,
        action_type=RuleActionType.VALIDATE,
        condition={"asset_type": "PUMP"},
        action={"validate": {"severity": "ERROR", "message": "Test"}},
        is_active=True
    )
    rule2 = RuleDefinition(
        id="rule-validation-2",
        name="Dummy Validation Rule 2",
        source=RuleSource.FIRM,
        priority=10,
        action_type=RuleActionType.VALIDATE,
        condition={"asset_type": "PUMP"},
        action={"validate": {"severity": "WARNING", "message": "Test"}},
        is_active=True
    )
    db_session.add(rule1)
    db_session.add(rule2)
    db_session.commit()

    # Create some execution logs
    exec1 = RuleExecution(
        rule_id=rule1.id,
        project_id=test_project.id,
        asset_id=pump_asset.id,
        action_type="VALIDATION_FAIL",
        action_taken="Error 1",
        error_message="Error 1"
    )
    exec2 = RuleExecution(
        rule_id=rule2.id,
        project_id=test_project.id,
        asset_id=pump_asset.id,
        action_type="VALIDATION_WARN",
        action_taken="Warn 1",
        error_message="Warn 1"
    )
    db_session.add(exec1)
    db_session.add(exec2)
    db_session.commit()

    # Test Summary
    summary = ValidationService.get_validation_summary(db_session,test_project.id)
    assert summary["errors"] >= 1
    assert summary["warnings"] >= 1
    assert summary["total_issues"] >= 2

    # Test Details
    details = ValidationService.get_validation_details(db_session,test_project.id)
    assert len(details) >= 2

    # Check if our created logs are in the details
    ids = [d["id"] for d in details]
    assert exec1.id in ids
    assert exec2.id in ids

    # Cleanup
    db_session.delete(rule1)
    db_session.delete(rule2)
    db_session.commit()
