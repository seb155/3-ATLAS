"""
DevConsole V3 Integration Tests

Tests the full stack of DevConsole functionality:
- ActionLogger
- WorkflowEngine
- WebSocket logging
- Log enrichment
- Filtering logic validation

These tests PROVE what works and what doesn't.
"""

import asyncio
from datetime import datetime

import pytest

from app.services.action_logger import action_logger
from app.services.workflow_engine import workflow_engine

# Mock storage for logs
mock_logs = []

def mock_websocket_log(log_dict):
    """Mock function that captures all log calls"""
    # Add timestamp if missing
    if "timestamp" not in log_dict:
        log_dict["timestamp"] = datetime.now().isoformat()
    mock_logs.append(log_dict)

class MockWebSocketLogger:
    log = staticmethod(mock_websocket_log)

@pytest.fixture(autouse=True)
def setup_mocks():
    """Setup mocks for each test"""
    global mock_logs
    mock_logs = []

    # Patch websocket_logger
    import app.services.action_logger as action_logger_module
    import app.services.workflow_engine as workflow_engine_module

    action_logger_module.websocket_logger = MockWebSocketLogger
    workflow_engine_module.websocket_logger = MockWebSocketLogger

    # Clear state
    action_logger.active_actions = {}
    workflow_engine.active_workflows = {}
    workflow_engine.templates = {}

    yield

    mock_logs = []


# ============================================================================
# ActionLogger Tests - CRITICAL FEATURES
# ============================================================================

@pytest.mark.asyncio
async def test_start_action_creates_unique_id():
    """VERIFY: start_action() creates unique action_id"""
    action_id = action_logger.start_action(
        action_type="TEST",
        summary="Test Action"
    )

    assert action_id is not None
    assert isinstance(action_id, str)
    assert len(action_id) > 0
    assert action_id in action_logger.active_actions


@pytest.mark.asyncio
async def test_log_step_includes_action_id():
    """VERIFY: log_step() includes actionId for grouping"""
    action_id = action_logger.start_action("TEST", "Test")

    action_logger.log_step(action_id, "Step 1")

    # Find step log
    step_logs = [log for log in mock_logs if log.get("message") == "Step 1"]
    assert len(step_logs) == 1
    assert step_logs[0]["actionId"] == action_id


@pytest.mark.asyncio
async def test_complete_action_updates_status():
    """VERIFY: complete_action() sets status to COMPLETED"""
    action_id = action_logger.start_action("TEST", "Test")
    action_logger.complete_action(action_id, stats={"items": 5})

    # Find completion log
    complete_logs = [log for log in mock_logs if log.get("actionStatus") == "COMPLETED"]
    assert len(complete_logs) == 1
    assert complete_logs[0]["actionId"] == action_id
    assert complete_logs[0]["actionStats"]["items"] == 5


@pytest.mark.asyncio
async def test_fail_action_sets_error():
    """VERIFY: fail_action() sets status to FAILED with error"""
    action_id = action_logger.start_action("TEST", "Test")
    action_logger.fail_action(action_id, "Something broke")

    # Find failure log
    fail_logs = [log for log in mock_logs if log.get("actionStatus") == "FAILED"]
    assert len(fail_logs) == 1
    assert fail_logs[0]["actionId"] == action_id
    assert "Something broke" in fail_logs[0]["message"]


@pytest.mark.asyncio
async def test_action_stats_calculation():
    """VERIFY: Stats are correctly calculated (duration, items)"""
    action_id = action_logger.start_action("TEST", "Test")

    # Simulate some work
    await asyncio.sleep(0.1)

    action_logger.complete_action(action_id, stats={"itemsProcessed": 10})

    # Find completion log
    complete_logs = [log for log in mock_logs if log.get("actionStatus") == "COMPLETED"]
    assert len(complete_logs) == 1

    stats = complete_logs[0]["actionStats"]
    assert "duration" in stats
    assert stats["duration"] >= 100  # At least 100ms
    assert stats["itemsProcessed"] == 10


@pytest.mark.asyncio
async def test_update_progress_changes_percentage():
    """VERIFY: update_progress() sends progress updates"""
    action_id = action_logger.start_action("TEST", "Test")

    action_logger.update_progress(action_id, 0.5, "50% done")

    # Find progress log
    progress_logs = [log for log in mock_logs if "actionProgress" in log]
    assert len(progress_logs) == 1
    assert progress_logs[0]["actionProgress"] == 0.5
    assert "50% done" in progress_logs[0]["message"]


# ============================================================================
# Entity Navigation Tests - CRITICAL FOR DEVCON SOLE
# ============================================================================

@pytest.mark.asyncio
async def test_entity_tag_included_in_log():
    """VERIFY: Entity tags (P-101) are included for navigation"""
    action_id = action_logger.start_action("TEST", "Test")

    action_logger.log_step(
        action_id,
        "Created pump",
        entity_tag="P-101",
        entity_route="/assets/123"
    )

    # Find log with entity
    entity_logs = [log for log in mock_logs if log.get("entityTag") == "P-101"]
    assert len(entity_logs) == 1
    assert entity_logs[0]["entityRoute"] == "/assets/123"


@pytest.mark.asyncio
async def test_entity_type_tracking():
    """VERIFY: Entity types are tracked (Asset, Cable, Rule)"""
    action_id = action_logger.start_action("TEST", "Test")

    action_logger.log_step(
        action_id,
        "Created asset",
        entity_tag="P-101",
        entity_type="Asset",
        entity_id="asset-123"
    )

    entity_logs = [log for log in mock_logs if log.get("entityType")]
    assert len(entity_logs) == 1
    assert entity_logs[0]["entityType"] == "Asset"
    assert entity_logs[0]["entityId"] == "asset-123"


# ============================================================================
# User Context Tests - FOR FILTERING
# ============================================================================

@pytest.mark.asyncio
async def test_user_id_and_name_tracking():
    """VERIFY: User ID and name are tracked for filtering"""
    action_id = action_logger.start_action(
        "TEST",
        "Test",
        user_id="user123",
        user_name="admin@aurumax.com"
    )

    # Find start log
    start_logs = [log for log in mock_logs if log.get("actionStatus") == "RUNNING"]
    assert len(start_logs) == 1
    assert start_logs[0]["userId"] == "user123"
    assert start_logs[0]["userName"] == "admin@aurumax.com"


# ============================================================================
# Topic & Discipline Tests - FOR FILTERING
# ============================================================================

@pytest.mark.asyncio
async def test_topic_tagging():
    """VERIFY: Topics (ASSETS, RULES, CABLES) are tagged"""
    action_id = action_logger.start_action(
        "IMPORT",
        "Import Assets",
        topic="ASSETS"
    )

    start_logs = [log for log in mock_logs if log.get("actionStatus") == "RUNNING"]
    assert len(start_logs) == 1
    assert start_logs[0]["topic"] == "ASSETS"


@pytest.mark.asyncio
async def test_discipline_tagging():
    """VERIFY: Disciplines (PROCESS, ELECTRICAL) are tagged"""
    action_id = action_logger.start_action(
        "RULE_EXECUTION",
        "Run Electrical Rules",
        discipline="ELECTRICAL"
    )

    start_logs = [log for log in mock_logs if log.get("actionStatus") == "RUNNING"]
    assert len(start_logs) == 1
    assert start_logs[0]["discipline"] == "ELECTRICAL"


# ============================================================================
# WorkflowEngine Tests - MULTI-JOB WORKFLOWS
# ============================================================================

@pytest.mark.asyncio
async def test_workflow_sequential_execution():
    """VERIFY: Jobs execute in sequence, not parallel"""
    execution_order = []

    async def job1(job_id, params):
        execution_order.append(1)
        await asyncio.sleep(0.05)
        return {"items": 5}

    async def job2(job_id, params):
        execution_order.append(2)
        return {"items": 3}

    workflow_engine.register_template("TEST_SEQ", [
        {"name": "Job 1", "function": job1},
        {"name": "Job 2", "function": job2}
    ])

    workflow_id = workflow_engine.start_workflow("TEST_SEQ", "Sequential Test", {})
    await workflow_engine.execute_workflow(workflow_id)

    # Verify order
    assert execution_order == [1, 2], "Jobs must execute sequentially"


@pytest.mark.asyncio
async def test_workflow_stops_on_failure():
    """VERIFY: Workflow stops if a job fails"""
    async def job_ok(job_id, params):
        return {}

    async def job_fail(job_id, params):
        raise ValueError("Job failed!")

    async def job_skip(job_id, params):
        pytest.fail("This job should not run!")
        return {}

    workflow_engine.register_template("TEST_FAIL", [
        {"name": "OK", "function": job_ok},
        {"name": "FAIL", "function": job_fail},
        {"name": "SKIP", "function": job_skip}
    ])

    workflow_id = workflow_engine.start_workflow("TEST_FAIL", "Fail Test", {})
    await workflow_engine.execute_workflow(workflow_id)

    # Verify SKIP job was NOT called (would have triggered pytest.fail)
    fail_logs = [log for log in mock_logs if log.get("actionStatus") == "FAILED"]
    assert len(fail_logs) >= 1  # At least the job failed


@pytest.mark.asyncio
async def test_workflow_aggregates_stats():
    """VERIFY: Workflow totals are calculated correctly"""
    async def job1(job_id, params):
        return {"items": 10}

    async def job2(job_id, params):
        return {"items": 5}

    workflow_engine.register_template("TEST_STATS", [
        {"name": "Job 1", "function": job1},
        {"name": "Job 2", "function": job2}
    ])

    workflow_id = workflow_engine.start_workflow("TEST_STATS", "Stats Test", {})
    await workflow_engine.execute_workflow(workflow_id)

    # Find workflow completion
    complete_logs = [
        log for log in mock_logs
        if log.get("actionStatus") == "COMPLETED"
        and log.get("actionType") == "TEST_STATS"
    ]
    assert len(complete_logs) == 1

    stats = complete_logs[0]["actionStats"]
    if stats.get("itemsProcessed") != 15:
        print(f"\nDEBUG: Expected 15 items, got {stats.get('itemsProcessed')}")
        print(f"DEBUG: Stats object: {stats}")

    assert stats["itemsProcessed"] == 15  # 10 + 5


# ============================================================================
# Nested Actions (Parent/Child) Tests
# ============================================================================

@pytest.mark.asyncio
async def test_nested_actions_parent_child():
    """VERIFY: Child actions link to parent via parentId"""
    parent_id = action_logger.start_action("PARENT", "Parent Action")
    child_id = action_logger.start_action(
        "CHILD",
        "Child Action",
        parent_action_id=parent_id
    )

    # Find child log
    child_logs = [log for log in mock_logs if log.get("actionSummary") == "Child Action"]
    assert len(child_logs) == 1
    assert child_logs[0]["parentId"] == parent_id


# ============================================================================
# Log Isolation Tests - CRITICAL FOR FILTERING
# ============================================================================

@pytest.mark.asyncio
async def test_orphan_logs_without_action():
    """VERIFY: Logs without actionId still work (standalone logs)"""
    # Try to log step for non-existent action
    action_logger.log_step("fake-id", "Standalone log", level="WARNING")

    # Should still create a log, just without actionId grouping
    standalone_logs = [log for log in mock_logs if log.get("message") == "Standalone log"]
    assert len(standalone_logs) == 1
    assert standalone_logs[0]["level"] == "WARNING"


# ============================================================================
# Real-World Scenario Test - IMPORT WORKFLOW
# ============================================================================

@pytest.mark.asyncio
async def test_realistic_import_workflow():
    """
    VERIFY: Full import workflow as it would happen in prod

    This tests:
    - Workflow creation
    - Multiple jobs
    - Entity tagging
    - Stats aggregation
    - Completion
    """
    async def fetch_external_data(job_id, params):
        action_logger.log_step(job_id, "Fetching from API...", level="INFO")
        await asyncio.sleep(0.01)
        action_logger.log_step(job_id, "Received 3 assets", level="INFO")
        return {"items": 3}

    async def create_assets(job_id, params):
        # Simulate creating 3 assets
        for tag in ["P-101", "P-102", "M-101"]:
            action_logger.log_step(
                job_id,
                f"Created {tag}",
                entity_tag=tag,
                entity_route=f"/assets/{tag}",
                entity_type="Asset"
            )
        return {"items": 3}

    async def update_database(job_id, params):
        action_logger.log_step(job_id, "Committing to database...")
        await asyncio.sleep(0.01)
        return {"items": 3}

    workflow_engine.register_template("IMPORT_GOLD_MINE", [
        {"name": "Fetch External Data", "function": fetch_external_data},
        {"name": "Create Assets", "function": create_assets},
        {"name": "Update Database", "function": update_database}
    ])

    workflow_id = workflow_engine.start_workflow(
        "IMPORT_GOLD_MINE",
        "Import Gold Mine Project",
        params={},
        user_id="admin",
        user_name="admin@aurumax.com"
    )

    await workflow_engine.execute_workflow(workflow_id)

    # Verify workflow completed
    complete_logs = [
        log for log in mock_logs
        if log.get("actionStatus") == "COMPLETED"
        and log.get("actionType") == "IMPORT_GOLD_MINE"
    ]
    assert len(complete_logs) == 1
    assert complete_logs[0]["actionStats"]["itemsProcessed"] == 9  # 3+3+3

    # Verify entity tags were logged
    entity_logs = [log for log in mock_logs if log.get("entityTag")]

    if len(entity_logs) != 3:
        print(f"\nDEBUG: Found {len(entity_logs)} entity logs:")
        for l in entity_logs:
            print(f" - {l.get('entityTag')} (Action: {l.get('actionId')})")

    assert len(entity_logs) == 3  # P-101, P-102, M-101

    tags = [log["entityTag"] for log in entity_logs]
    assert "P-102" in tags
    assert "M-101" in tags


# ============================================================================
# Performance Test - LOG VOLUME
# ============================================================================

@pytest.mark.asyncio
async def test_high_volume_logging():
    """VERIFY: System handles high log volume (1000+ logs)"""
    action_id = action_logger.start_action("BULK", "Bulk Test")

    # Generate 1000 logs
    for i in range(1000):
        action_logger.log_step(action_id, f"Step {i}")

    action_logger.complete_action(action_id)

    # Verify all logs were captured
    assert len(mock_logs) >= 1000  # 1000 steps + start + complete

    # Verify they all have the same actionId
    action_logs = [log for log in mock_logs if log.get("actionId") == action_id]
    assert len(action_logs) >= 1000
