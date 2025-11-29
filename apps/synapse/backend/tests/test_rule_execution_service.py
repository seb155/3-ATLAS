"""
Tests for RuleExecutionService with Workflow Events and Versioning

Tests the new rule execution pipeline with:
- WorkflowLogger integration
- VersioningService integration
- All 7 action types
- Batch operations support
- Event sourcing pattern
"""

from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from app.models.auth import Client, Project, User
from app.models.models import Asset
from app.models.rules import RuleActionType, RuleDefinition, RuleSource
from app.models.workflow import (
    AssetVersion,
    BatchOperation,
    BatchOperationType,
    ChangeSource,
    LogSource,
    WorkflowActionType,
    WorkflowEvent,
)
from app.services.rule_execution_service import RuleExecutionService
from app.services.versioning_service import VersioningService
from app.services.workflow_logger import WorkflowLogger

# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def test_client(db_session: Session):
    """Create test client"""
    client = Client(
        id=f"test-client-{uuid4().hex[:8]}",
        name="Test Client"
    )
    db_session.add(client)
    db_session.commit()
    return client


@pytest.fixture
def test_user(db_session: Session):
    """Create test user"""
    user = User(
        id=f"test-user-{uuid4().hex[:8]}",
        email="test@example.com",
        hashed_password="hashed",
        full_name="Test User"
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def test_project(db_session: Session, test_client):
    """Create test project"""
    project = Project(
        id=f"test-project-{uuid4().hex[:8]}",
        name="Test Project",
        client_id=test_client.id,
        country="CA",
    )
    db_session.add(project)
    db_session.commit()
    return project


@pytest.fixture
def test_pump(db_session: Session, test_project):
    """Create test pump asset"""
    pump = Asset(
        id=f"pump-{uuid4().hex[:8]}",
        tag="310-PP-001",
        type="PUMP",
        project_id=test_project.id,
        area="310",
        system="PROCESS",
        properties={"pump_type": "CENTRIFUGAL", "power_kw": 75},
    )
    db_session.add(pump)
    db_session.commit()
    return pump


@pytest.fixture
def create_child_rule(db_session: Session):
    """Create a CREATE_CHILD rule for testing"""
    rule = RuleDefinition(
        id=f"rule-{uuid4().hex[:8]}",
        name="Test: Pump requires Motor",
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
                "properties": {"motor_type": "Electric"}
            }
        },
        is_active=True,
    )
    db_session.add(rule)
    db_session.commit()
    db_session.refresh(rule)
    return rule


@pytest.fixture
def set_property_rule(db_session: Session):
    """Create a SET_PROPERTY rule for testing"""
    rule = RuleDefinition(
        id=f"rule-{uuid4().hex[:8]}",
        name="Test: Set Motor Voltage",
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
def create_package_rule(db_session: Session):
    """Create a CREATE_PACKAGE rule for testing"""
    rule = RuleDefinition(
        id=f"rule-{uuid4().hex[:8]}",
        name="Test: Create Electrical Package",
        source=RuleSource.FIRM,
        priority=20,
        discipline="ELECTRICAL",
        action_type=RuleActionType.CREATE_PACKAGE,
        condition={"discipline": "ELECTRICAL"},
        action={
            "create_package": {
                "naming": "PKG-{discipline}-{area}",
                "group_by": ["discipline", "area"]
            }
        },
        is_active=True,
    )
    db_session.add(rule)
    db_session.commit()
    db_session.refresh(rule)
    return rule


# ============================================================================
# WorkflowLogger Tests
# ============================================================================

class TestWorkflowLogger:
    """Tests for WorkflowLogger service"""

    def test_start_workflow_returns_correlation_id(self, db_session: Session, test_project, test_user):
        """Test that starting a workflow returns a correlation ID"""
        logger = WorkflowLogger(
            db=db_session,
            project_id=test_project.id,
            user_id=test_user.id
        )

        correlation_id = logger.start_workflow(
            source=LogSource.RULE,
            action_type=WorkflowActionType.EXECUTE,
            message="Test workflow started"
        )

        assert correlation_id is not None
        assert isinstance(correlation_id, str)
        assert len(correlation_id) > 0

    def test_workflow_event_persisted(self, db_session: Session, test_project, test_user):
        """Test workflow event is persisted to database"""
        logger = WorkflowLogger(
            db=db_session,
            project_id=test_project.id,
            user_id=test_user.id
        )

        correlation_id = logger.start_workflow(
            source=LogSource.RULE,
            action_type=WorkflowActionType.EXECUTE,
            message="Test workflow started"
        )

        # Force flush to database
        db_session.flush()

        # Query for event
        events = db_session.query(WorkflowEvent).filter(
            WorkflowEvent.correlation_id == correlation_id
        ).all()

        assert len(events) >= 1

    def test_log_event_with_correlation(self, db_session: Session, test_project, test_user):
        """Test that log_event uses correlation ID"""
        logger = WorkflowLogger(
            db=db_session,
            project_id=test_project.id,
            user_id=test_user.id
        )

        correlation_id = logger.start_workflow(
            source=LogSource.RULE,
            action_type=WorkflowActionType.EXECUTE,
            message="Parent workflow"
        )

        # Log a child event
        logger.log_info(
            message="Child event",
            source=LogSource.RULE,
            correlation_id=correlation_id
        )

        db_session.flush()

        # Both events should have same correlation_id
        events = db_session.query(WorkflowEvent).filter(
            WorkflowEvent.correlation_id == correlation_id
        ).all()

        assert len(events) == 2


# ============================================================================
# VersioningService Tests
# ============================================================================

class TestVersioningService:
    """Tests for VersioningService"""

    def test_create_version(self, db_session: Session, test_project, test_pump, test_user):
        """Test creating a version of an asset"""
        service = VersioningService(
            db=db_session,
            project_id=test_project.id,
            user_id=test_user.id
        )

        version = service.create_version(
            asset=test_pump,
            change_source=ChangeSource.IMPORT
        )

        assert version is not None
        assert version.asset_id == test_pump.id
        assert version.version_number >= 1
        assert version.change_source == ChangeSource.IMPORT
        assert "tag" in version.snapshot
        assert version.snapshot["tag"] == "310-PP-001"

    def test_version_numbers_increment(self, db_session: Session, test_project, test_pump, test_user):
        """Test that version numbers increment correctly"""
        service = VersioningService(
            db=db_session,
            project_id=test_project.id,
            user_id=test_user.id
        )

        v1 = service.create_version(test_pump, ChangeSource.USER)
        v2 = service.create_version(test_pump, ChangeSource.USER, change_reason="Updated")

        assert v2.version_number == v1.version_number + 1

    def test_get_asset_versions(self, db_session: Session, test_project, test_pump, test_user):
        """Test retrieving asset version history"""
        service = VersioningService(
            db=db_session,
            project_id=test_project.id,
            user_id=test_user.id
        )

        service.create_version(test_pump, ChangeSource.IMPORT)

        versions = service.get_asset_versions(test_pump.id)

        assert len(versions) == 1
        assert versions[0].asset_id == test_pump.id


# ============================================================================
# RuleExecutionService Tests
# ============================================================================

class TestRuleExecutionService:
    """Tests for RuleExecutionService"""

    def test_execute_creates_workflow_events(
        self, db_session: Session, test_project, test_pump, create_child_rule, test_user
    ):
        """Test that rule execution creates workflow events"""
        service = RuleExecutionService(
            db=db_session,
            project_id=test_project.id,
            user_id=test_user.id
        )

        # Execute with asset IDs (not objects)
        result = service.execute_rules(asset_ids=[test_pump.id])

        # Check workflow events were created
        events = db_session.query(WorkflowEvent).filter(
            WorkflowEvent.project_id == test_project.id,
            WorkflowEvent.source == LogSource.RULE
        ).all()

        assert len(events) >= 1
        assert result.total_assets >= 1

    def test_create_child_action(
        self, db_session: Session, test_project, test_pump, create_child_rule, test_user
    ):
        """Test CREATE_CHILD action creates child asset"""
        service = RuleExecutionService(
            db=db_session,
            project_id=test_project.id,
            user_id=test_user.id
        )

        service.execute_rules(asset_ids=[test_pump.id])

        # Check motor was created
        motor = db_session.query(Asset).filter(
            Asset.tag == "310-PP-001-M",
            Asset.project_id == test_project.id
        ).first()

        assert motor is not None
        assert motor.type == "MOTOR"

    def test_create_child_idempotency(
        self, db_session: Session, test_project, test_pump, create_child_rule, test_user
    ):
        """Test CREATE_CHILD is idempotent"""
        service = RuleExecutionService(
            db=db_session,
            project_id=test_project.id,
            user_id=test_user.id
        )

        # Execute twice
        service.execute_rules(asset_ids=[test_pump.id])
        service.execute_rules(asset_ids=[test_pump.id])

        # Should only have one motor
        motors = db_session.query(Asset).filter(
            Asset.tag == "310-PP-001-M",
            Asset.project_id == test_project.id
        ).all()

        assert len(motors) == 1

    def test_set_property_action(
        self, db_session: Session, test_project, test_user, set_property_rule
    ):
        """Test SET_PROPERTY action sets properties"""
        # Create a motor
        motor = Asset(
            id=f"motor-{uuid4().hex[:8]}",
            tag="310-PP-001-M",
            type="MOTOR",
            project_id=test_project.id,
            properties={},
        )
        db_session.add(motor)
        db_session.commit()

        service = RuleExecutionService(
            db=db_session,
            project_id=test_project.id,
            user_id=test_user.id
        )

        service.execute_rules(asset_ids=[motor.id])

        db_session.refresh(motor)
        assert motor.properties.get("voltage") == "600V"
        assert motor.properties.get("frequency") == "60Hz"

    def test_set_property_creates_version(
        self, db_session: Session, test_project, test_user, set_property_rule
    ):
        """Test SET_PROPERTY creates asset version"""
        motor = Asset(
            id=f"motor-{uuid4().hex[:8]}",
            tag="310-PP-001-M",
            type="MOTOR",
            project_id=test_project.id,
            properties={},
        )
        db_session.add(motor)
        db_session.commit()

        service = RuleExecutionService(
            db=db_session,
            project_id=test_project.id,
            user_id=test_user.id
        )

        service.execute_rules(asset_ids=[motor.id])

        # Check version was created
        versions = db_session.query(AssetVersion).filter(
            AssetVersion.asset_id == motor.id
        ).all()

        assert len(versions) >= 1

    def test_condition_matching(
        self, db_session: Session, test_project, test_pump, create_child_rule, test_user
    ):
        """Test condition matching works correctly"""
        # Create a tank (should not match pump rule)
        tank = Asset(
            id=f"tank-{uuid4().hex[:8]}",
            tag="310-TK-001",
            type="TANK",
            project_id=test_project.id,
        )
        db_session.add(tank)
        db_session.commit()

        service = RuleExecutionService(
            db=db_session,
            project_id=test_project.id,
            user_id=test_user.id
        )

        service.execute_rules(asset_ids=[tank.id])

        # No motor should be created for tank
        motors = db_session.query(Asset).filter(
            Asset.tag.like("310-TK-001-%"),
            Asset.type == "MOTOR"
        ).all()

        assert len(motors) == 0

    def test_batch_operation_tracking(
        self, db_session: Session, test_project, test_pump, create_child_rule, test_user
    ):
        """Test batch operations are tracked"""
        service = RuleExecutionService(
            db=db_session,
            project_id=test_project.id,
            user_id=test_user.id
        )

        service.execute_rules(asset_ids=[test_pump.id])

        # Check batch operation was created
        batches = db_session.query(BatchOperation).filter(
            BatchOperation.project_id == test_project.id,
            BatchOperation.operation_type == BatchOperationType.RULE_EXECUTION
        ).all()

        assert len(batches) >= 1

    def test_execute_returns_summary(
        self, db_session: Session, test_project, test_pump, create_child_rule, test_user
    ):
        """Test execute_rules returns proper summary"""
        service = RuleExecutionService(
            db=db_session,
            project_id=test_project.id,
            user_id=test_user.id
        )

        result = service.execute_rules(asset_ids=[test_pump.id])

        assert hasattr(result, 'total_rules')
        assert hasattr(result, 'total_assets')
        assert hasattr(result, 'actions_taken')
        assert hasattr(result, 'errors')


# ============================================================================
# Property Filter Tests
# ============================================================================

class TestPropertyFilters:
    """Tests for property filter conditions"""

    def test_equals_operator(
        self, db_session: Session, test_project, test_user
    ):
        """Test == operator in property filters"""
        rule = RuleDefinition(
            id=f"rule-{uuid4().hex[:8]}",
            name="Filter Test",
            source=RuleSource.FIRM,
            priority=10,
            action_type=RuleActionType.SET_PROPERTY,
            condition={
                "asset_type": "PUMP",
                "property_filters": [
                    {"key": "pump_type", "op": "==", "value": "CENTRIFUGAL"}
                ]
            },
            action={"set_property": {"filtered": "true"}},
            is_active=True,
        )
        db_session.add(rule)

        pump1 = Asset(
            id=f"pump-{uuid4().hex[:8]}",
            tag="PUMP-001",
            type="PUMP",
            project_id=test_project.id,
            properties={"pump_type": "CENTRIFUGAL"},
        )
        pump2 = Asset(
            id=f"pump-{uuid4().hex[:8]}",
            tag="PUMP-002",
            type="PUMP",
            project_id=test_project.id,
            properties={"pump_type": "POSITIVE_DISPLACEMENT"},
        )
        db_session.add_all([pump1, pump2])
        db_session.commit()

        service = RuleExecutionService(
            db=db_session,
            project_id=test_project.id,
            user_id=test_user.id
        )

        service.execute_rules(asset_ids=[pump1.id, pump2.id])

        db_session.refresh(pump1)
        db_session.refresh(pump2)

        assert pump1.properties.get("filtered") == "true"
        assert pump2.properties.get("filtered") is None

    def test_greater_than_operator(
        self, db_session: Session, test_project, test_user
    ):
        """Test > operator in property filters"""
        rule = RuleDefinition(
            id=f"rule-{uuid4().hex[:8]}",
            name="Power Filter",
            source=RuleSource.FIRM,
            priority=10,
            action_type=RuleActionType.SET_PROPERTY,
            condition={
                "asset_type": "PUMP",
                "property_filters": [
                    {"key": "power_kw", "op": ">", "value": 50}
                ]
            },
            action={"set_property": {"high_power": "true"}},
            is_active=True,
        )
        db_session.add(rule)

        pump1 = Asset(
            id=f"pump-{uuid4().hex[:8]}",
            tag="PUMP-HIGH",
            type="PUMP",
            project_id=test_project.id,
            properties={"power_kw": 100},
        )
        pump2 = Asset(
            id=f"pump-{uuid4().hex[:8]}",
            tag="PUMP-LOW",
            type="PUMP",
            project_id=test_project.id,
            properties={"power_kw": 25},
        )
        db_session.add_all([pump1, pump2])
        db_session.commit()

        service = RuleExecutionService(
            db=db_session,
            project_id=test_project.id,
            user_id=test_user.id
        )

        service.execute_rules(asset_ids=[pump1.id, pump2.id])

        db_session.refresh(pump1)
        db_session.refresh(pump2)

        assert pump1.properties.get("high_power") == "true"
        assert pump2.properties.get("high_power") is None

    def test_in_operator(
        self, db_session: Session, test_project, test_user
    ):
        """Test in operator in property filters"""
        rule = RuleDefinition(
            id=f"rule-{uuid4().hex[:8]}",
            name="Area Filter",
            source=RuleSource.FIRM,
            priority=10,
            action_type=RuleActionType.SET_PROPERTY,
            condition={
                "asset_type": "PUMP",
                "property_filters": [
                    {"key": "area", "op": "in", "value": ["310", "320"]}
                ]
            },
            action={"set_property": {"in_area": "true"}},
            is_active=True,
        )
        db_session.add(rule)

        pump1 = Asset(
            id=f"pump-{uuid4().hex[:8]}",
            tag="310-PP-001",
            type="PUMP",
            project_id=test_project.id,
            area="310",
        )
        pump2 = Asset(
            id=f"pump-{uuid4().hex[:8]}",
            tag="400-PP-001",
            type="PUMP",
            project_id=test_project.id,
            area="400",
        )
        db_session.add_all([pump1, pump2])
        db_session.commit()

        service = RuleExecutionService(
            db=db_session,
            project_id=test_project.id,
            user_id=test_user.id
        )

        service.execute_rules(asset_ids=[pump1.id, pump2.id])

        db_session.refresh(pump1)
        db_session.refresh(pump2)

        assert (pump1.properties or {}).get("in_area") == "true"
        assert (pump2.properties or {}).get("in_area") is None


# ============================================================================
# Error Handling Tests
# ============================================================================

class TestErrorHandling:
    """Tests for error handling in rule execution"""

    def test_invalid_action_handled(
        self, db_session: Session, test_project, test_pump, test_user
    ):
        """Test invalid action configuration is handled gracefully"""
        bad_rule = RuleDefinition(
            id=f"rule-{uuid4().hex[:8]}",
            name="Bad Rule",
            source=RuleSource.FIRM,
            priority=10,
            action_type=RuleActionType.CREATE_CHILD,
            condition={"asset_type": "PUMP"},
            action={},  # Missing create_child config
            is_active=True,
        )
        db_session.add(bad_rule)
        db_session.commit()

        service = RuleExecutionService(
            db=db_session,
            project_id=test_project.id,
            user_id=test_user.id
        )

        # Should complete without crashing
        result = service.execute_rules(asset_ids=[test_pump.id])

        assert result is not None
        assert result.errors >= 1

    def test_missing_asset_handled(
        self, db_session: Session, test_project, create_child_rule, test_user
    ):
        """Test missing asset is handled gracefully"""
        service = RuleExecutionService(
            db=db_session,
            project_id=test_project.id,
            user_id=test_user.id
        )

        # Should not crash with non-existent asset ID
        result = service.execute_rules(asset_ids=["non-existent-id"])
        assert result is not None
