"""
Workflow Logger Service

Provides a unified interface for logging all workflow events with:
- Database persistence (workflow_events table)
- WebSocket real-time broadcast
- Correlation tracking for related events
- Hierarchical event grouping (parent/child)
- Breakdown filtering (FBS, LBS, discipline)

Usage:
    from app.services.workflow_logger import WorkflowLogger

    # Start a workflow (e.g., CSV import)
    logger = WorkflowLogger(db, project_id, user_id)
    correlation_id = logger.start_workflow(
        source=LogSource.IMPORT,
        action_type=WorkflowActionType.IMPORT,
        message="Importing BBA-Instruments.csv"
    )

    # Log individual events within the workflow
    logger.log_event(
        source=LogSource.IMPORT,
        action_type=WorkflowActionType.CREATE,
        message="Created asset LT-210-001",
        entity_type="ASSET",
        entity_tag="LT-210-001",
        correlation_id=correlation_id
    )

    # Complete the workflow
    logger.complete_workflow(correlation_id, duration_ms=1234)

Design based on: .dev/design/2025-11-28-whiteboard-session.md
"""

import time
import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.workflow import (
    BatchOperation,
    BatchOperationType,
    LogLevel,
    LogSource,
    WorkflowActionType,
    WorkflowEvent,
    WorkflowStatus,
)
from app.services.websocket_manager import websocket_logger


def generate_correlation_id() -> str:
    """Generate a unique correlation ID for grouping related events."""
    return str(uuid.uuid4())


class WorkflowLogger:
    """
    Unified workflow event logger.

    Logs events to both:
    - PostgreSQL (workflow_events table) for persistence & querying
    - WebSocket for real-time DevConsole updates
    """

    def __init__(
        self,
        db: Session,
        project_id: str,
        user_id: str | None = None,
        session_id: str | None = None,
    ):
        """
        Initialize the workflow logger.

        Args:
            db: Database session
            project_id: Current project context
            user_id: User performing the action (optional)
            session_id: Browser session ID for grouping (optional)
        """
        self.db = db
        self.project_id = project_id
        self.user_id = user_id
        self.session_id = session_id or str(uuid.uuid4())
        self._active_workflows: dict[str, dict] = {}

    def start_workflow(
        self,
        source: LogSource,
        action_type: WorkflowActionType,
        message: str,
        entity_type: str | None = None,
        entity_id: str | None = None,
        entity_tag: str | None = None,
        details: dict | None = None,
        fbs_code: str | None = None,
        lbs_code: str | None = None,
        discipline: str | None = None,
        package_code: str | None = None,
    ) -> str:
        """
        Start a new workflow and return its correlation_id.

        A workflow groups related events (e.g., one CSV import = many asset creates).

        Args:
            source: Event source (IMPORT, RULE, USER, etc.)
            action_type: Type of action (CREATE, EXECUTE, etc.)
            message: Human-readable description
            entity_type: Type of entity being acted on (optional)
            entity_id: Entity ID (optional)
            entity_tag: Human-readable tag like "LT-210-001" (optional)
            details: Additional structured data (optional)
            fbs_code: Functional breakdown code (optional)
            lbs_code: Location breakdown code (optional)
            discipline: Engineering discipline (optional)
            package_code: Work package code (optional)

        Returns:
            correlation_id for this workflow
        """
        correlation_id = generate_correlation_id()

        # Create root event
        event = self._create_event(
            level=LogLevel.INFO,
            source=source,
            action_type=action_type,
            message=message,
            entity_type=entity_type,
            entity_id=entity_id,
            entity_tag=entity_tag,
            details=details,
            correlation_id=correlation_id,
            status=WorkflowStatus.IN_PROGRESS,
            fbs_code=fbs_code,
            lbs_code=lbs_code,
            discipline=discipline,
            package_code=package_code,
        )

        # Track active workflow
        self._active_workflows[correlation_id] = {
            "root_event_id": event.id,
            "start_time": time.time(),
            "message": message,
            "source": source,
        }

        # Broadcast to WebSocket
        self._broadcast_event(event, is_start=True)

        return correlation_id

    def log_event(
        self,
        source: LogSource,
        action_type: WorkflowActionType,
        message: str,
        correlation_id: str,
        level: LogLevel = LogLevel.INFO,
        entity_type: str | None = None,
        entity_id: str | None = None,
        entity_tag: str | None = None,
        details: dict | None = None,
        parent_event_id: str | None = None,
        status: WorkflowStatus = WorkflowStatus.COMPLETED,
        duration_ms: int | None = None,
        error: str | None = None,
        fbs_code: str | None = None,
        lbs_code: str | None = None,
        discipline: str | None = None,
        package_code: str | None = None,
    ) -> WorkflowEvent:
        """
        Log an individual event within a workflow.

        Args:
            source: Event source
            action_type: Type of action
            message: Human-readable description
            correlation_id: Workflow this event belongs to
            level: Log level (INFO, WARN, ERROR, etc.)
            entity_type: Type of entity (ASSET, CABLE, RULE, etc.)
            entity_id: Entity ID
            entity_tag: Human-readable tag
            details: Additional structured data
            parent_event_id: Parent event for nesting
            status: Event status
            duration_ms: Operation duration in milliseconds
            error: Error message if status is FAILED
            fbs_code: Functional breakdown code
            lbs_code: Location breakdown code
            discipline: Engineering discipline
            package_code: Work package code

        Returns:
            Created WorkflowEvent
        """
        # If no parent specified and workflow is active, use root event
        if parent_event_id is None and correlation_id in self._active_workflows:
            parent_event_id = self._active_workflows[correlation_id]["root_event_id"]

        event = self._create_event(
            level=level,
            source=source,
            action_type=action_type,
            message=message,
            entity_type=entity_type,
            entity_id=entity_id,
            entity_tag=entity_tag,
            details=details,
            correlation_id=correlation_id,
            parent_event_id=parent_event_id,
            status=status,
            duration_ms=duration_ms,
            error=error,
            fbs_code=fbs_code,
            lbs_code=lbs_code,
            discipline=discipline,
            package_code=package_code,
        )

        # Broadcast to WebSocket
        self._broadcast_event(event)

        return event

    def complete_workflow(
        self,
        correlation_id: str,
        duration_ms: int | None = None,
        stats: dict | None = None,
    ) -> WorkflowEvent | None:
        """
        Mark a workflow as completed.

        Args:
            correlation_id: Workflow to complete
            duration_ms: Total duration (auto-calculated if not provided)
            stats: Summary statistics

        Returns:
            Completion event or None if workflow not found
        """
        if correlation_id not in self._active_workflows:
            return None

        workflow = self._active_workflows[correlation_id]

        # Calculate duration if not provided
        if duration_ms is None:
            duration_ms = int((time.time() - workflow["start_time"]) * 1000)

        # Create completion event
        event = self.log_event(
            source=workflow["source"],
            action_type=WorkflowActionType.EXECUTE,
            message=f"Completed: {workflow['message']}",
            correlation_id=correlation_id,
            level=LogLevel.INFO,
            status=WorkflowStatus.COMPLETED,
            duration_ms=duration_ms,
            details=stats,
        )

        # Update root event status
        root_event = (
            self.db.query(WorkflowEvent)
            .filter(WorkflowEvent.id == workflow["root_event_id"])
            .first()
        )
        if root_event:
            root_event.status = WorkflowStatus.COMPLETED
            root_event.duration_ms = duration_ms
            self.db.commit()

        # Remove from active workflows
        del self._active_workflows[correlation_id]

        return event

    def fail_workflow(
        self,
        correlation_id: str,
        error: str,
        duration_ms: int | None = None,
    ) -> WorkflowEvent | None:
        """
        Mark a workflow as failed.

        Args:
            correlation_id: Workflow that failed
            error: Error message
            duration_ms: Duration until failure

        Returns:
            Failure event or None if workflow not found
        """
        if correlation_id not in self._active_workflows:
            return None

        workflow = self._active_workflows[correlation_id]

        # Calculate duration if not provided
        if duration_ms is None:
            duration_ms = int((time.time() - workflow["start_time"]) * 1000)

        # Create failure event
        event = self.log_event(
            source=workflow["source"],
            action_type=WorkflowActionType.EXECUTE,
            message=f"Failed: {workflow['message']}",
            correlation_id=correlation_id,
            level=LogLevel.ERROR,
            status=WorkflowStatus.FAILED,
            duration_ms=duration_ms,
            error=error,
        )

        # Update root event status
        root_event = (
            self.db.query(WorkflowEvent)
            .filter(WorkflowEvent.id == workflow["root_event_id"])
            .first()
        )
        if root_event:
            root_event.status = WorkflowStatus.FAILED
            root_event.duration_ms = duration_ms
            root_event.error = error
            self.db.commit()

        # Remove from active workflows
        del self._active_workflows[correlation_id]

        return event

    def _create_event(
        self,
        level: LogLevel,
        source: LogSource,
        action_type: WorkflowActionType,
        message: str,
        correlation_id: str,
        entity_type: str | None = None,
        entity_id: str | None = None,
        entity_tag: str | None = None,
        details: dict | None = None,
        parent_event_id: str | None = None,
        status: WorkflowStatus = WorkflowStatus.COMPLETED,
        duration_ms: int | None = None,
        error: str | None = None,
        fbs_code: str | None = None,
        lbs_code: str | None = None,
        discipline: str | None = None,
        package_code: str | None = None,
    ) -> WorkflowEvent:
        """Create and persist a workflow event."""
        event = WorkflowEvent(
            level=level,
            source=source,
            action_type=action_type,
            project_id=self.project_id,
            user_id=self.user_id,
            session_id=self.session_id,
            entity_type=entity_type,
            entity_id=entity_id,
            entity_tag=entity_tag,
            message=message,
            details=details or {},
            parent_event_id=parent_event_id,
            correlation_id=correlation_id,
            status=status,
            duration_ms=duration_ms,
            error=error,
            fbs_code=fbs_code,
            lbs_code=lbs_code,
            discipline=discipline,
            package_code=package_code,
        )

        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)

        return event

    def _broadcast_event(self, event: WorkflowEvent, is_start: bool = False):
        """Broadcast event to WebSocket clients."""
        try:
            payload = {
                "id": event.id,
                "timestamp": event.timestamp.isoformat()
                if event.timestamp
                else datetime.utcnow().isoformat(),
                "level": event.level.value,
                "source": event.source.value,
                "actionType": event.action_type.value,
                "message": event.message,
                "status": event.status.value,
                "entityType": event.entity_type,
                "entityId": event.entity_id,
                "entityTag": event.entity_tag,
                "correlationId": event.correlation_id,
                "parentEventId": event.parent_event_id,
                "durationMs": event.duration_ms,
                "error": event.error,
                "details": event.details,
                "fbsCode": event.fbs_code,
                "lbsCode": event.lbs_code,
                "discipline": event.discipline,
                "packageCode": event.package_code,
                "isWorkflowStart": is_start,
            }

            websocket_logger.log(payload)
        except Exception:
            # Don't fail the main operation if WebSocket broadcast fails
            pass

    # ==========================================================================
    # CONVENIENCE METHODS
    # ==========================================================================

    def log_info(
        self,
        message: str,
        correlation_id: str,
        source: LogSource = LogSource.SYSTEM,
        **kwargs,
    ) -> WorkflowEvent:
        """Log an INFO level event."""
        return self.log_event(
            source=source,
            action_type=WorkflowActionType.EXECUTE,
            message=message,
            correlation_id=correlation_id,
            level=LogLevel.INFO,
            **kwargs,
        )

    def log_warning(
        self,
        message: str,
        correlation_id: str,
        source: LogSource = LogSource.SYSTEM,
        **kwargs,
    ) -> WorkflowEvent:
        """Log a WARNING level event."""
        return self.log_event(
            source=source,
            action_type=WorkflowActionType.VALIDATE,
            message=message,
            correlation_id=correlation_id,
            level=LogLevel.WARN,
            **kwargs,
        )

    def log_error(
        self,
        message: str,
        correlation_id: str,
        error: str,
        source: LogSource = LogSource.SYSTEM,
        **kwargs,
    ) -> WorkflowEvent:
        """Log an ERROR level event."""
        return self.log_event(
            source=source,
            action_type=WorkflowActionType.EXECUTE,
            message=message,
            correlation_id=correlation_id,
            level=LogLevel.ERROR,
            status=WorkflowStatus.FAILED,
            error=error,
            **kwargs,
        )

    def log_create(
        self,
        entity_type: str,
        entity_id: str,
        entity_tag: str,
        correlation_id: str,
        source: LogSource = LogSource.RULE,
        message: str | None = None,
        **kwargs,
    ) -> WorkflowEvent:
        """Log a CREATE action."""
        return self.log_event(
            source=source,
            action_type=WorkflowActionType.CREATE,
            message=message or f"Created {entity_type}: {entity_tag}",
            correlation_id=correlation_id,
            entity_type=entity_type,
            entity_id=entity_id,
            entity_tag=entity_tag,
            **kwargs,
        )

    def log_update(
        self,
        entity_type: str,
        entity_id: str,
        entity_tag: str,
        correlation_id: str,
        source: LogSource = LogSource.USER,
        message: str | None = None,
        details: dict | None = None,
        **kwargs,
    ) -> WorkflowEvent:
        """Log an UPDATE action with before/after details."""
        return self.log_event(
            source=source,
            action_type=WorkflowActionType.UPDATE,
            message=message or f"Updated {entity_type}: {entity_tag}",
            correlation_id=correlation_id,
            entity_type=entity_type,
            entity_id=entity_id,
            entity_tag=entity_tag,
            details=details,
            **kwargs,
        )

    def log_delete(
        self,
        entity_type: str,
        entity_id: str,
        entity_tag: str,
        correlation_id: str,
        source: LogSource = LogSource.USER,
        message: str | None = None,
        **kwargs,
    ) -> WorkflowEvent:
        """Log a DELETE action."""
        return self.log_event(
            source=source,
            action_type=WorkflowActionType.DELETE,
            message=message or f"Deleted {entity_type}: {entity_tag}",
            correlation_id=correlation_id,
            entity_type=entity_type,
            entity_id=entity_id,
            entity_tag=entity_tag,
            **kwargs,
        )


# =============================================================================
# BATCH OPERATIONS
# =============================================================================


class BatchOperationManager:
    """
    Manages batch operations for bulk rollback support.

    Example:
        manager = BatchOperationManager(db, project_id, user_id)
        batch = manager.start_batch(
            operation_type=BatchOperationType.IMPORT,
            description="Import BBA-Instruments.csv"
        )
        # ... perform operations ...
        manager.complete_batch(batch.id, affected_assets=100)
    """

    def __init__(self, db: Session, project_id: str, user_id: str | None = None):
        self.db = db
        self.project_id = project_id
        self.user_id = user_id

    def start_batch(
        self,
        operation_type: BatchOperationType,
        description: str,
        correlation_id: str | None = None,
    ) -> BatchOperation:
        """
        Start a new batch operation.

        Args:
            operation_type: Type of batch operation
            description: Human-readable description
            correlation_id: Workflow correlation ID (auto-generated if not provided)

        Returns:
            Created BatchOperation
        """
        batch = BatchOperation(
            operation_type=operation_type,
            description=description,
            project_id=self.project_id,
            created_by=self.user_id,
            correlation_id=correlation_id or generate_correlation_id(),
        )

        self.db.add(batch)
        self.db.commit()
        self.db.refresh(batch)

        return batch

    def complete_batch(
        self,
        batch_id: str,
        affected_assets: int,
    ) -> BatchOperation | None:
        """
        Mark a batch operation as completed.

        Args:
            batch_id: Batch to complete
            affected_assets: Number of assets affected

        Returns:
            Updated BatchOperation or None if not found
        """
        batch = self.db.query(BatchOperation).filter(BatchOperation.id == batch_id).first()
        if not batch:
            return None

        batch.completed_at = datetime.utcnow()
        batch.affected_assets = affected_assets
        self.db.commit()

        return batch

    def rollback_batch(
        self,
        batch_id: str,
        reason: str,
        rolled_back_by: str | None = None,
    ) -> BatchOperation | None:
        """
        Mark a batch operation as rolled back.

        Args:
            batch_id: Batch to rollback
            reason: Reason for rollback
            rolled_back_by: User performing the rollback

        Returns:
            Updated BatchOperation or None if not found
        """
        batch = self.db.query(BatchOperation).filter(BatchOperation.id == batch_id).first()
        if not batch:
            return None

        batch.is_rolled_back = True
        batch.rolled_back_at = datetime.utcnow()
        batch.rolled_back_by = rolled_back_by or self.user_id
        batch.rollback_reason = reason
        self.db.commit()

        return batch


# =============================================================================
# STATIC HELPER (Backward Compatibility)
# =============================================================================


def log_workflow_event(
    db: Session,
    project_id: str,
    source: LogSource,
    action_type: WorkflowActionType,
    message: str,
    user_id: str | None = None,
    correlation_id: str | None = None,
    **kwargs,
) -> WorkflowEvent:
    """
    Static helper for one-off event logging.

    For workflows with multiple related events, use WorkflowLogger class instead.
    """
    logger = WorkflowLogger(db, project_id, user_id)
    return logger.log_event(
        source=source,
        action_type=action_type,
        message=message,
        correlation_id=correlation_id or generate_correlation_id(),
        **kwargs,
    )
