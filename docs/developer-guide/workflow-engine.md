# Workflow Engine - Developer Guide

**Purpose**: Orchestrate multi-step operations as hierarchical workflows

---

## Overview

The Workflow Engine provides a simple way to organize multi-step operations (imports, rule executions, exports) into **workflows** with clear job phases and step tracking.

**Not a job scheduler**: Uses FastAPI BackgroundTasks for simplicity. Can migrate to Celery later if needed.

---

## Concepts

### 3-Level Hierarchy

```
WORKFLOW: User-initiated action (Import, Export, Rule Execution)
  └─ JOB: Phase of the workflow (Fetch, Process, Validate, Save)
      └─ STEP: Individual operation (Created P-101, Updated M-102)
```

### Workflow Lifecycle

```
START → RUNNING → COMPLETED
              ↓
            FAILED (on first job failure)
```

Jobs run **sequentially**:
- Job 2 starts only after Job 1 completes
- If Job 2 fails, Jobs 3-4 are cancelled
- User is notified immediately on failure

---

## Backend Usage

### 1. Import Example

```python
# apps/synapse/backend/app/api/endpoints/assets.py

from fastapi import BackgroundTasks
from app.services.workflow_engine import workflow_engine
from app.services.action_logger import action_logger

@router.post("/import")
async def import_assets(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    # Save uploaded file
    file_path = await save_upload(file)
    
    # Create workflow
    workflow_id = workflow_engine.start_workflow(
        workflow_type="IMPORT_ASSETS",
        params={
            "file_path": file_path,
            "user_id": current_user.id
        },
        user=current_user
    )
    
    # Execute in background
    background_tasks.add_task(
        workflow_engine.execute_workflow,
        workflow_id
    )
    
    # Return immediately (don't block user)
    return {
        "workflow_id": workflow_id,
        "status": "RUNNING",
        "message": "Import started"
    }
```

### 2. Workflow Definition

```python
# apps/synapse/backend/app/services/workflows/import_assets.py

async def import_assets_workflow(workflow_id: str, params: dict):
    """
    Workflow for importing assets.
    
    Jobs:
    1. Fetch External Assets
    2. Process Data
    3. Validate
    4. Save to Database
    """
    
    # Job 1: Fetch
    job1_id = action_logger.start_action(
        "FETCH_EXTERNAL",
        "Fetch External Assets",
        userId=params["user_id"],
        topic="IMPORT"
    )
    
    try:
        assets = await fetch_external_assets(params["file_path"])
        
        for asset in assets:
            action_logger.log_step(
                job1_id,
                f"Fetched {asset['tag']}",
                entity_tag=asset["tag"]
            )
        
        action_logger.complete_action(job1_id, stats={
            "itemsFetched": len(assets)
        })
    except Exception as e:
        action_logger.fail_action(job1_id, str(e))
        raise
    
    # Job 2: Process
    job2_id = action_logger.start_action(
        "PROCESS_DATA",
        "Process Data",
        userId=params["user_id"]
    )
    
    try:
        processed = await process_assets(assets)
        action_logger.complete_action(job2_id, stats={
            "itemsProcessed": len(processed)
        })
    except Exception as e:
        action_logger.fail_action(job2_id, str(e))
        raise  # Stop workflow
    
    # Job 3: Validate
    # ... similar pattern
    
    # Job 4: Save
    # ... similar pattern
    
    return {"status": "COMPLETED", "items": len(assets)}
```

### 3. Workflow Template System

```python
# apps/synapse/backend/app/services/workflow_engine.py

WORKFLOW_TEMPLATES = {
    "IMPORT_ASSETS": {
        "jobs": [
            {"name": "Fetch External", "function": "import_assets.fetch"},
            {"name": "Process Data", "function": "import_assets.process"},
            {"name": "Validate", "function": "import_assets.validate"},
            {"name": "Save to DB", "function": "import_assets.save"}
        ]
    },
    "RULE_EXECUTION": {
        "jobs": [
            {"name": "Load Rules", "function": "rules.load"},
            {"name": "Execute", "function": "rules.execute"},
            {"name": "Apply Results", "function": "rules.apply"}
        ]
    },
    "EXPORT_PACKAGE": {
        "jobs": [
            {"name": "Gather Data", "function": "export.gather"},
            {"name": "Generate Excel", "function": "export.excel"},
            {"name": "Generate PDF", "function": "export.pdf"}
        ]
    }
}
```

---

## ActionLogger API

### Start Action (Job)
```python
action_id = action_logger.start_action(
    action_type="IMPORT",
    summary="Import Gold Mine",
    user_id=current_user.id,
    user_name=current_user.email,
    topic="IMPORT",
    discipline="PROJECT"
)
```

### Log Step
```python
action_logger.log_step(
    action_id,
    message="Created P-101",
    level="INFO",
    entity_tag="P-101",
    entity_route="/assets/123",
    entity_id="123",
    entity_type="Asset"
)
```

### Update Progress
```python
action_logger.update_progress(
    action_id,
    progress=0.5,  # 50%
    message="Processing 50/100 items"
)
```

### Complete Action
```python
action_logger.complete_action(
    action_id,
    stats={
        "duration": 2300,  # ms (auto-calculated if not provided)
        "itemsProcessed": 100,
        "itemsCreated": 95,
        "itemsFailed": 5
    }
)
```

### Fail Action
```python
action_logger.fail_action(
    action_id,
    error="Database connection lost",
    stack=traceback.format_exc()
)
```

---

## Frontend Integration

### useDevConsole Hook

```typescript
import { useDevConsole } from '@/components/DevConsoleV3/hooks/useDevConsole';

function MyComponent() {
  const { 
    filteredWorkflows,  // Grouped workflows
    selectedLog,        // Selected item
    setSelectedLog,     // Select function
  } = useDevConsole();
  
  return (
    <div>
      {filteredWorkflows.map(workflow => (
        <WorkflowItem 
          key={workflow.id}
          workflow={workflow}
          onSelect={setSelectedLog}
        />
      ))}
    </div>
  );
}
```

### Workflow Structure

```typescript
interface Workflow {
  id: string;
  type: string;              // "IMPORT_ASSETS"
  summary: string;           // "Import Gold Mine"
  status: "RUNNING" | "COMPLETED" | "FAILED";
  timestamp: string;
  userId: string;
  userName: string;
  jobs: Job[];
  stats?: {
    duration: number;
    itemsProcessed: number;
  };
}

interface Job {
  id: string;
  name: string;             // "Fetch External"
  status: "RUNNING" | "COMPLETED" | "FAILED" | "PENDING";
  steps: Step[];
  stats?: {
    duration: number;
    items: number;
  };
}

interface Step {
  id: string;
  message: string;          // "Created P-101"
  level: "DEBUG" | "INFO" | "WARN" | "ERROR";
  entityTag?: string;       // "P-101"
  entityRoute?: string;     // "/assets/123"
}
```

---

## Best Practices

### 1. Granular Steps
✅ **Good**: Clear, actionable steps
```python
action_logger.log_step(job_id, "Created asset P-101", entity_tag="P-101")
action_logger.log_step(job_id, "Linked P-101 → M-101")
action_logger.log_step(job_id, "Generated cable C-001")
```

❌ **Bad**: Vague steps
```python
action_logger.log_step(job_id, "Processing...")
action_logger.log_step(job_id, "Done")
```

### 2. Meaningful Job Names
✅ **Good**: Describes the phase
```python
"Fetch External Assets"
"Process Data"
"Validate Schemas"
```

❌ **Bad**: Too generic
```python
"Step 1"
"Do stuff"
"Execute"
```

### 3. Include Entity Navigation
✅ **Good**: Provides navigation
```python
action_logger.log_step(
    job_id,
    "Created P-101",
    entity_tag="P-101",
    entity_route="/assets/123"
)
```

❌ **Bad**: No navigation
```python
action_logger.log_step(job_id, "Created asset")
```

### 4. Provide Stats
✅ **Good**: Summary stats
```python
action_logger.complete_action(job_id, stats={
    "itemsProcessed": 100,
    "itemsCreated": 95,
    "itemsFailed": 5,
    "duration": 2300
})
```

❌ **Bad**: No stats
```python
action_logger.complete_action(job_id)
```

---

## Error Handling

### Fail Fast
When a job fails, **stop the workflow immediately**:

```python
try:
    result = await process_data(assets)
    action_logger.complete_action(job_id)
except Exception as e:
    action_logger.fail_action(job_id, str(e), traceback.format_exc())
    
    # Notify user via WebSocket
    await websocket_logger.notify_error(
        workflow_id,
        f"Workflow failed at: {job_name}",
        error=str(e),
        action="VIEW_DETAILS"
    )
    
    raise  # Stop workflow
```

### User Notification
Frontend shows notification:
```
❌ Workflow Failed
Import Gold Mine failed at "Process Data"
Error: Invalid schema for P-101

[View Details]  [Retry]
```

---

## Performance Considerations

### Logging Overhead
- Each `log_step()`: ~2-5ms
- WebSocket broadcast: <10ms
- Total overhead: <1% of workflow time

### Batching Steps
For bulk operations, batch logs:

✅ **Good**: Batch + summary
```python
# Process 1000 items
for i in range(0, 1000, 100):
    batch = items[i:i+100]
    process_batch(batch)
    
    # Log every 100 items
    action_logger.update_progress(
        job_id,
        progress=i/1000,
        message=f"Processed {i}/1000 items"
    )

# Final summary
action_logger.complete_action(job_id, stats={"items": 1000})
```

❌ **Bad**: Log every item (10000 logs!)
```python
for item in items:  # 1000 items
    process(item)
    action_logger.log_step(job_id, f"Processed {item}")
```

---

## Testing

### Unit Tests
```python
# tests/test_workflow_engine.py

def test_workflow_completes():
    workflow_id = workflow_engine.start_workflow("TEST", {})
    result = await workflow_engine.execute_workflow(workflow_id)
    
    assert result["status"] == "COMPLETED"
    
def test_workflow_fails_on_error():
    workflow_id = workflow_engine.start_workflow("TEST_FAIL", {})
    
    with pytest.raises(Exception):
        await workflow_engine.execute_workflow(workflow_id)
    
    workflow = get_workflow(workflow_id)
    assert workflow.status == "FAILED"
```

### Integration Tests
Test with DevConsole open:
1. Start workflow
2. Verify WebSocket receives logs
3. Check timeline shows workflow
4. Verify stats are correct

---

## Migration to Celery (Future)

When workflows exceed 5 minutes, migrate to Celery:

```python
# Before (FastAPI BackgroundTasks)
background_tasks.add_task(workflow_engine.execute_workflow, workflow_id)

# After (Celery)
from app.tasks import execute_workflow_task
execute_workflow_task.delay(workflow_id)
```

**Frontend**: No changes needed! Same workflow structure.

---

## Related Documentation

- [DevConsole V3 Reference](../reference/devconsole-v3.md)
- [Logging Infrastructure](../reference/logging-infrastructure.md)
- [ADR-002: DevConsole Architecture](../../.dev/decisions/002-devconsole-v3-architecture.md)
