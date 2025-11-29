"""
Task Submission API

Endpoints for submitting and managing tasks.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum
import uuid

router = APIRouter()


class TaskStatus(str, Enum):
    """Task status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskCreate(BaseModel):
    """Request model for creating a task."""
    session_id: str
    description: str
    context_blocks: List[str] = []
    require_confirmation: bool = True
    max_iterations: int = 20


class TaskResponse(BaseModel):
    """Response model for task data."""
    id: str
    session_id: str
    description: str
    status: TaskStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    result: Optional[str] = None
    iterations: int = 0
    context_blocks: List[str] = []


# In-memory storage for MVP
tasks_store: dict = {}


@router.post("/", response_model=TaskResponse)
async def create_task(task: TaskCreate, background_tasks: BackgroundTasks):
    """Submit a new task for execution."""
    task_id = str(uuid.uuid4())
    now = datetime.utcnow()

    task_data = {
        "id": task_id,
        "session_id": task.session_id,
        "description": task.description,
        "status": TaskStatus.PENDING,
        "created_at": now,
        "completed_at": None,
        "result": None,
        "iterations": 0,
        "context_blocks": task.context_blocks,
    }

    tasks_store[task_id] = task_data

    # TODO: Add to job queue for async execution
    # background_tasks.add_task(execute_task, task_id)

    return TaskResponse(**task_data)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str):
    """Get task details and status."""
    if task_id not in tasks_store:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse(**tasks_store[task_id])


@router.get("/session/{session_id}", response_model=List[TaskResponse])
async def list_session_tasks(session_id: str):
    """List all tasks for a session."""
    session_tasks = [
        TaskResponse(**t) for t in tasks_store.values()
        if t["session_id"] == session_id
    ]
    return session_tasks


@router.post("/{task_id}/cancel")
async def cancel_task(task_id: str):
    """Cancel a running task."""
    if task_id not in tasks_store:
        raise HTTPException(status_code=404, detail="Task not found")

    task = tasks_store[task_id]
    if task["status"] not in [TaskStatus.PENDING, TaskStatus.RUNNING]:
        raise HTTPException(status_code=400, detail="Task cannot be cancelled")

    task["status"] = TaskStatus.CANCELLED
    return {"status": "cancelled", "task_id": task_id}
