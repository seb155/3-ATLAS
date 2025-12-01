import pytest

from app.services.action_logger import action_logger
from app.services.workflow_engine import workflow_engine

# Mock storage for logs
mock_logs = []


# Simple mock that captures log calls (synchronous)
def mock_websocket_log(log_dict):
    """Mock function that captures all log calls - accepts dict as arg"""
    mock_logs.append(log_dict)


# Mock WebSocketLogger class
class MockWebSocketLogger:
    log = staticmethod(mock_websocket_log)


@pytest.fixture(autouse=True)
def setup_mocks():
    """Setup mocks for each test"""
    global mock_logs
    mock_logs = []

    # Patch websocket_logger in both modules
    import app.services.action_logger as action_logger_module
    import app.services.workflow_engine as workflow_engine_module

    action_logger_module.websocket_logger = MockWebSocketLogger
    workflow_engine_module.websocket_logger = MockWebSocketLogger

    # Clear action logger state
    action_logger.active_actions = {}

    yield

    # Cleanup
    mock_logs = []


@pytest.mark.asyncio
async def test_action_logger_lifecycle():
    """Test full lifecycle of an action: Start -> Log Step -> Complete"""

    # 1. Start Action
    action_id = action_logger.start_action(
        action_type="TEST", summary="Test Action", user_id="user123"
    )

    assert action_id is not None
    assert action_id in action_logger.active_actions
    assert len(mock_logs) == 1
    assert mock_logs[0]["actionStatus"] == "RUNNING"

    # 2. Log Step
    action_logger.log_step(action_id, "Step 1", entity_tag="E-1")

    assert len(mock_logs) == 2
    assert mock_logs[1]["message"] == "Step 1"
    assert mock_logs[1]["entityTag"] == "E-1"

    # 3. Complete Action
    action_logger.complete_action(action_id, stats={"items": 10})

    assert action_id not in action_logger.active_actions
    assert len(mock_logs) == 3
    assert mock_logs[2]["actionStatus"] == "COMPLETED"
    assert mock_logs[2]["actionStats"]["items"] == 10


@pytest.mark.asyncio
async def test_workflow_engine_execution():
    """Test workflow execution with mock jobs"""

    # Define mock jobs
    async def job1(job_id, params):
        action_logger.log_step(job_id, "Job 1 running")
        return {"items": 5}

    async def job2(job_id, params):
        action_logger.log_step(job_id, "Job 2 running")
        return {"items": 3}

    # Register template
    workflow_engine.register_template(
        "TEST_WORKFLOW", [{"name": "Job 1", "function": job1}, {"name": "Job 2", "function": job2}]
    )

    # Start Workflow
    workflow_id = workflow_engine.start_workflow("TEST_WORKFLOW", "Test Workflow", params={})

    # Execute
    await workflow_engine.execute_workflow(workflow_id)

    # Verify
    logs = mock_logs

    # Should have at least 8 logs
    assert len(logs) >= 8

    # Check final status
    workflow_complete_log = logs[-1]
    assert workflow_complete_log["actionStatus"] == "COMPLETED"
    assert workflow_complete_log["actionStats"]["itemsProcessed"] == 8  # 5 + 3


@pytest.mark.asyncio
async def test_workflow_failure():
    """Test workflow stops on job failure"""

    async def job_success(job_id, params):
        return {}

    async def job_fail(job_id, params):
        raise ValueError("Job Failed!")

    async def job_skipped(job_id, params):
        return {}

    workflow_engine.register_template(
        "FAIL_WORKFLOW",
        [
            {"name": "Success", "function": job_success},
            {"name": "Fail", "function": job_fail},
            {"name": "Skipped", "function": job_skipped},
        ],
    )

    workflow_id = workflow_engine.start_workflow("FAIL_WORKFLOW", "Fail Test", {})
    await workflow_engine.execute_workflow(workflow_id)

    logs = mock_logs
    last_log = logs[-1]

    assert last_log["actionStatus"] == "FAILED"
    assert "Job Failed!" in last_log["message"]

    # Verify job_skipped was NOT run
    job_names = [l.get("actionSummary") for l in logs if l.get("actionType") == "JOB"]
    assert "Success" in job_names
    assert "Fail" in job_names
    assert "Skipped" not in job_names
