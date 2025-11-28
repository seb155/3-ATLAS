"""
Action Logger Service for DevConsole V3

Groups related logs into workflows for better UX.
Instead of showing 50 individual log entries for an import,
we group them into ONE workflow with jobs and steps.

Example:
    from app.services.action_logger import action_logger

    action_id = action_logger.start_action("IMPORT", "Import Gold Mine")
    action_logger.log_step(action_id, "Created P-101", entity_tag="P-101")
    action_logger.complete_action(action_id, stats={"itemsCreated": 15})
"""

import uuid
from datetime import datetime
from typing import Any

from app.services.websocket_manager import websocket_logger


class ActionLogger:
    """
    Groups related logs into hierarchical workflows.

    Workflows have:
    - Summary (e.g., "Import Gold Mine")
    - Status (RUNNING, COMPLETED, FAILED)
    - Stats (duration, items processed, etc.)
    - Child logs (individual steps)
    """

    def __init__(self):
        self.active_actions: dict[str, dict[str, Any]] = {}

    def start_action(
        self,
        action_type: str,
        summary: str,
        user_id: str | None = None,
        user_name: str | None = None,
        topic: str | None = None,
        discipline: str | None = None,
        parent_action_id: str | None = None,
    ) -> str:
        """
        Start a new action group.

        Args:
            action_type: Type of action (IMPORT, RULE_EXECUTION, CRUD, etc.)
            summary: Human-readable summary (e.g., "Import Gold Mine Data")
            user_id: User who triggered this action
            user_name: User's display name (email)
            topic: Log topic (ASSETS, RULES, etc.)
            discipline: Engineering discipline
            parent_action_id: Parent action if nested

        Returns:
            action_id: Unique identifier for this action
        """
        action_id = str(uuid.uuid4())

        self.active_actions[action_id] = {
            "id": action_id,
            "type": action_type,
            "summary": summary,
            "status": "RUNNING",
            "startTime": datetime.now(),
            "steps": [],
        }

        # Log action start to WebSocket
        websocket_logger.log(
            {
                "level": "INFO",
                "message": f"▶ Started: {summary}",
                "source": "BACKEND",
                "actionId": action_id,
                "actionType": action_type,
                "actionSummary": summary,
                "actionStatus": "RUNNING",
                "userId": user_id,
                "userName": user_name,
                "topic": topic or "SYSTEM",
                "discipline": discipline,
                "parentId": parent_action_id,
            }
        )

        return action_id

    def log_step(
        self,
        action_id: str,
        message: str,
        level: str = "INFO",
        entity_tag: str | None = None,
        entity_route: str | None = None,
        entity_id: str | None = None,
        entity_type: str | None = None,
        **kwargs,
    ):
        """
        Add a step to an action.

        Args:
            action_id: Action this step belongs to
            message: Step description
            level: Log level (DEBUG, INFO, WARN, ERROR)
            entity_tag: Human-readable entity tag (e.g., "P-101")
            entity_route: Navigation route (e.g., "/assets/123")
            entity_id: Entity ID for backend tracking
            entity_type: Entity type (Asset, Cable, Rule, etc.)
            **kwargs: Additional context
        """
        if action_id not in self.active_actions:
            # Action might have been completed/failed already
            # Still log the step as standalone
            websocket_logger.log(
                {
                    "level": level,
                    "message": message,
                    "source": "BACKEND",
                    "entityTag": entity_tag,
                    "entityRoute": entity_route,
                    "entityId": entity_id,
                    "entityType": entity_type,
                    "context": kwargs,
                }
            )
            return

        # Log step with parent action_id
        websocket_logger.log(
            {
                "level": level,
                "message": message,
                "source": "BACKEND",
                "actionId": action_id,
                "entityTag": entity_tag,
                "entityRoute": entity_route,
                "entityId": entity_id,
                "entityType": entity_type,
                "context": kwargs,
            }
        )

    def complete_action(self, action_id: str, stats: dict[str, Any] | None = None):
        """
        Mark action as completed with optional stats.

        Args:
            action_id: Action to complete
            stats: Summary statistics (duration, items processed, etc.)
        """
        if action_id not in self.active_actions:
            return

        action = self.active_actions[action_id]
        duration_ms = (datetime.now() - action["startTime"]).total_seconds() * 1000

        websocket_logger.log(
            {
                "level": "INFO",
                "message": f"✓ Completed: {action['summary']}",
                "source": "BACKEND",
                "actionId": action_id,
                "actionType": action["type"],
                "actionSummary": action["summary"],
                "actionStatus": "COMPLETED",
                "actionStats": {"duration": round(duration_ms, 2), **(stats or {})},
            }
        )

        del self.active_actions[action_id]

    def fail_action(self, action_id: str, error: str, stack: str | None = None):
        """
        Mark action as failed.

        Args:
            action_id: Action that failed
            error: Error message
            stack: Stack trace (optional)
        """
        if action_id not in self.active_actions:
            return

        action = self.active_actions[action_id]
        duration_ms = (datetime.now() - action["startTime"]).total_seconds() * 1000

        websocket_logger.log(
            {
                "level": "ERROR",
                "message": f"✗ Failed: {action['summary']} - {error}",
                "source": "BACKEND",
                "actionId": action_id,
                "actionType": action["type"],
                "actionSummary": action["summary"],
                "actionStatus": "FAILED",
                "actionStats": {"duration": round(duration_ms, 2)},
                "stack": stack,
            }
        )

        del self.active_actions[action_id]

    def update_progress(self, action_id: str, progress: float, message: str | None = None):
        """
        Update action progress (0.0 to 1.0).

        Args:
            action_id: Action to update
            progress: Progress percentage (0.0 - 1.0)
            message: Optional progress message
        """
        if action_id not in self.active_actions:
            return



        websocket_logger.log(
            {
                "level": "INFO",
                "message": message or f"Progress: {int(progress * 100)}%",
                "source": "BACKEND",
                "actionId": action_id,
                "actionStatus": "RUNNING",
                "actionProgress": progress,
            }
        )

    @staticmethod
    def log(db=None, action_type=None, description=None, payload: dict[str, Any] = None, **kwargs):
        """
        Static method for backward compatibility.
        Supports both old and new API signatures.

        Old positional API (rule_engine.py):
            ActionLogger.log(db, ActionType.CREATE, "description", ...)

        Old kwargs API:
            ActionLogger.log(db=db, action_type=..., description=..., ...)

        New API (websocket logging):
            ActionLogger.log(payload={"level": "INFO", ...})

        Args:
            db: Database session (old API)
            action_type: ActionType enum (old API)
            description: Description string (old API)
            payload: Log payload dictionary (new API)
            **kwargs: Additional named arguments

        Returns:
            ActionLog model instance if using old API with db parameter
        """
        # Old API: Database logging with ActionLog model (positional or kwargs)
        if db is not None:
            from app.models.action_log import ActionLog

            # Build kwargs for ActionLog
            log_kwargs = {
                'action_type': action_type,
                'description': description,
                **kwargs
            }

            action_log = ActionLog(**log_kwargs)
            db.add(action_log)
            db.commit()
            db.refresh(action_log)
            return action_log

        # New API: WebSocket logging
        if payload:
            websocket_logger.log(payload)
        elif action_type or description:
            # Fallback: convert to payload
            websocket_logger.log({
                'action_type': str(action_type) if action_type else None,
                'message': description,
                **kwargs
            })


# Global singleton instance
action_logger = ActionLogger()
