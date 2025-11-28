"""
Workflow Engine Service

Orchestrates multi-step operations (workflows) without an external job scheduler.
Uses FastAPI BackgroundTasks for async execution.

Concepts:
- Workflow: A high-level user action (e.g., "Import Assets")
- Job: A phase within the workflow (e.g., "Fetch Data", "Process")
- Step: A granular log entry within a job

Usage:
    workflow_id = workflow_engine.start_workflow("IMPORT", params)
    background_tasks.add_task(workflow_engine.execute_workflow, workflow_id)
"""

import traceback
from datetime import datetime
from typing import Any

from app.services.action_logger import action_logger


class WorkflowEngine:
    """
    Simple workflow orchestrator.
    Executes jobs sequentially and handles failures.
    """

    def __init__(self):
        # In-memory storage for active workflows (could be DB in future)
        self.active_workflows: dict[str, dict[str, Any]] = {}
        self.templates: dict[str, list[dict[str, Any]]] = {}

    def register_template(self, workflow_type: str, jobs: list[dict[str, Any]]):
        """
        Register a workflow template.

        Args:
            workflow_type: Unique identifier (e.g., "IMPORT_ASSETS")
            jobs: List of job definitions
                  [{"name": "Fetch", "function": async_func}, ...]
        """
        self.templates[workflow_type] = jobs

    def start_workflow(
        self,
        workflow_type: str,
        summary: str,
        params: dict[str, Any],
        user_id: str | None = None,
        user_name: str | None = None,
    ) -> str:
        """
        Initialize a new workflow.

        Returns:
            workflow_id: Unique ID for the workflow
        """
        workflow_id = action_logger.start_action(
            action_type=workflow_type,
            summary=summary,
            user_id=user_id,
            user_name=user_name,
            topic="WORKFLOW",
        )

        self.active_workflows[workflow_id] = {
            "id": workflow_id,
            "type": workflow_type,
            "params": params,
            "user_id": user_id,
            "status": "RUNNING",
            "startTime": datetime.now(),
        }

        return workflow_id

    async def execute_workflow(self, workflow_id: str):
        """
        Execute the workflow jobs sequentially.
        Should be run in background task.
        """
        if workflow_id not in self.active_workflows:
            return

        workflow = self.active_workflows[workflow_id]
        workflow_type = workflow["type"]
        params = workflow["params"]
        user_id = workflow["user_id"]

        # Get jobs from template
        jobs = self.templates.get(workflow_type, [])

        if not jobs:
            action_logger.fail_action(workflow_id, f"No template found for {workflow_type}")
            return

        try:
            total_items = 0

            for job_def in jobs:
                job_name = job_def["name"]
                job_func = job_def["function"]

                # Start Job
                job_id = action_logger.start_action(
                    action_type="JOB",
                    summary=job_name,
                    user_id=user_id,
                    parent_action_id=workflow_id,
                    topic=workflow_type,
                )

                try:
                    # Execute Job Function
                    # Function should accept (job_id, params)
                    result = await job_func(job_id, params)

                    # Complete Job
                    stats = result if isinstance(result, dict) else {}
                    action_logger.complete_action(job_id, stats=stats)

                    if "items" in stats:
                        total_items += stats["items"]

                except Exception as e:
                    # Fail Job
                    error_msg = str(e)
                    stack = traceback.format_exc()
                    action_logger.fail_action(job_id, error_msg, stack)

                    # Fail Workflow (Stop execution)
                    action_logger.fail_action(workflow_id, f"Failed at {job_name}: {error_msg}")
                    return

            # All jobs completed
            action_logger.complete_action(
                workflow_id, stats={"itemsProcessed": total_items, "jobsCompleted": len(jobs)}
            )

            # Cleanup
            if workflow_id in self.active_workflows:
                del self.active_workflows[workflow_id]

        except Exception as e:
            # Catastrophic failure
            action_logger.fail_action(workflow_id, str(e), traceback.format_exc())


# Global instance
workflow_engine = WorkflowEngine()
