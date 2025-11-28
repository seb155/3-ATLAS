# Rule Engine Event Sourcing - Technical Specification

**Version:** 1.0
**Date:** 2025-11-28
**Status:** Approved (ADR-003)

---

## Overview

This document provides the complete technical specification for implementing Event Sourcing in the SYNAPSE Rule Engine. It covers database models, services, API endpoints, WebSocket protocol, and frontend components.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Database Models](#database-models)
3. [Backend Services](#backend-services)
4. [API Endpoints](#api-endpoints)
5. [WebSocket Protocol](#websocket-protocol)
6. [Frontend Components](#frontend-components)
7. [Testing Strategy](#testing-strategy)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              SYNAPSE Rule Engine                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│  │   Frontend   │    │   FastAPI    │    │  PostgreSQL  │                  │
│  │    React     │◄──►│   Backend    │◄──►│   Database   │                  │
│  └──────────────┘    └──────────────┘    └──────────────┘                  │
│         │                   │                    │                          │
│         │              ┌────┴────┐          ┌────┴────┐                     │
│         │              │         │          │         │                     │
│    WebSocket      ┌────▼────┐ ┌──▼───┐  ┌───▼───┐ ┌───▼────┐              │
│    Real-time      │ Event   │ │Rule  │  │Events │ │Snapshot│              │
│                   │ Store   │ │Engine│  │ Table │ │ Table  │              │
│                   └─────────┘ └──────┘  └───────┘ └────────┘              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Key Concepts

| Concept | Description |
|---------|-------------|
| **Event** | Immutable record of something that happened |
| **Aggregate** | Entity being tracked (Asset, Cable, Edge, Rule) |
| **Correlation ID** | Groups events from same execution batch |
| **Causation ID** | Links effect event to its cause event |
| **Snapshot** | Pre-execution state for rollback capability |

---

## Database Models

### WorkflowEvent Model

**File:** `apps/synapse/backend/app/models/workflow_events.py`

```python
"""
Workflow Events - Event Sourcing for Rule Engine

Immutable event store for complete audit trail and traceability.
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey, Integer,
    String, Text, Index, BigInteger
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base


class WorkflowEventType(str, enum.Enum):
    """Types of workflow events"""

    # Asset events
    ASSET_CREATED = "ASSET_CREATED"
    ASSET_UPDATED = "ASSET_UPDATED"
    ASSET_DELETED = "ASSET_DELETED"

    # Cable events
    CABLE_CREATED = "CABLE_CREATED"
    CABLE_UPDATED = "CABLE_UPDATED"
    CABLE_DELETED = "CABLE_DELETED"

    # Relationship events
    RELATIONSHIP_CREATED = "RELATIONSHIP_CREATED"
    RELATIONSHIP_DELETED = "RELATIONSHIP_DELETED"

    # Rule execution events
    RULE_EXECUTION_STARTED = "RULE_EXECUTION_STARTED"
    RULE_EXECUTED = "RULE_EXECUTED"
    RULE_SKIPPED = "RULE_SKIPPED"
    RULE_ERROR = "RULE_ERROR"
    RULE_EXECUTION_COMPLETED = "RULE_EXECUTION_COMPLETED"

    # Batch events
    BATCH_STARTED = "BATCH_STARTED"
    BATCH_COMPLETED = "BATCH_COMPLETED"
    BATCH_ROLLED_BACK = "BATCH_ROLLED_BACK"

    # Import events
    CSV_IMPORTED = "CSV_IMPORTED"

    # System events
    ROLLBACK = "ROLLBACK"


class AggregateType(str, enum.Enum):
    """Types of aggregates (entities) being tracked"""

    ASSET = "ASSET"
    CABLE = "CABLE"
    EDGE = "EDGE"
    RULE = "RULE"
    PACKAGE = "PACKAGE"
    BATCH = "BATCH"


class WorkflowEvent(Base):
    """
    Immutable event record for workflow traceability.

    Events are append-only and never modified or deleted.
    They form the complete audit trail of all changes in the system.
    """

    __tablename__ = "workflow_events"

    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    # Event Identification
    event_type = Column(
        SQLEnum(WorkflowEventType),
        nullable=False,
        index=True
    )
    aggregate_type = Column(
        SQLEnum(AggregateType),
        nullable=False,
        index=True
    )
    aggregate_id = Column(String(100), nullable=True, index=True)

    # Context
    project_id = Column(
        String,
        ForeignKey("projects.id"),
        nullable=False,
        index=True
    )
    rule_id = Column(
        String,
        ForeignKey("rule_definitions.id"),
        nullable=True,
        index=True
    )
    discipline = Column(String(30), nullable=True, index=True)

    # Payload (before/after state, diff, context)
    payload = Column(JSONB, nullable=False, default=dict)
    metadata = Column(JSONB, nullable=True, default=dict)

    # Correlation (for batch operations)
    correlation_id = Column(
        UUID(as_uuid=True),
        nullable=False,
        index=True
    )
    causation_id = Column(UUID(as_uuid=True), nullable=True)
    sequence_num = Column(BigInteger, nullable=False, default=0)

    # Audit
    user_id = Column(
        String,
        ForeignKey("users.id"),
        nullable=True
    )
    timestamp = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        index=True
    )
    is_rolled_back = Column(Boolean, nullable=False, default=False)

    # Relationships
    project = relationship("Project")
    rule = relationship("RuleDefinition")
    user = relationship("User")

    # Composite indexes for common queries
    __table_args__ = (
        Index(
            'ix_workflow_events_project_time',
            'project_id', 'timestamp'
        ),
        Index(
            'ix_workflow_events_aggregate_lookup',
            'aggregate_type', 'aggregate_id', 'timestamp'
        ),
        Index(
            'ix_workflow_events_correlation_seq',
            'correlation_id', 'sequence_num'
        ),
    )

    def __repr__(self):
        return f"<WorkflowEvent {self.event_type.value} {self.aggregate_type.value}:{self.aggregate_id}>"

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "event_type": self.event_type.value,
            "aggregate_type": self.aggregate_type.value,
            "aggregate_id": self.aggregate_id,
            "project_id": self.project_id,
            "rule_id": self.rule_id,
            "discipline": self.discipline,
            "payload": self.payload,
            "metadata": self.metadata,
            "correlation_id": str(self.correlation_id),
            "causation_id": str(self.causation_id) if self.causation_id else None,
            "sequence_num": self.sequence_num,
            "user_id": self.user_id,
            "timestamp": self.timestamp.isoformat(),
            "is_rolled_back": self.is_rolled_back,
        }


class SnapshotStatus(str, enum.Enum):
    """Status of execution snapshot"""
    ACTIVE = "ACTIVE"
    ROLLED_BACK = "ROLLED_BACK"


class ExecutionSnapshot(Base):
    """
    Pre-execution snapshot for rollback capability.

    Captures the state of affected entities before a batch execution,
    allowing precise restoration if rollback is needed.
    """

    __tablename__ = "execution_snapshots"

    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    # Links to event batch
    correlation_id = Column(
        UUID(as_uuid=True),
        unique=True,
        nullable=False,
        index=True
    )
    project_id = Column(
        String,
        ForeignKey("projects.id"),
        nullable=False,
        index=True
    )

    # Snapshot data
    snapshot_data = Column(JSONB, nullable=False)
    events_count = Column(Integer, nullable=False, default=0)

    # Status
    status = Column(
        SQLEnum(SnapshotStatus),
        nullable=False,
        default=SnapshotStatus.ACTIVE,
        index=True
    )
    executed_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow
    )
    rolled_back_at = Column(DateTime(timezone=True), nullable=True)
    rolled_back_by = Column(
        String,
        ForeignKey("users.id"),
        nullable=True
    )

    # Relationships
    project = relationship("Project")
    rollback_user = relationship("User", foreign_keys=[rolled_back_by])

    def __repr__(self):
        return f"<ExecutionSnapshot {self.correlation_id} ({self.status.value})>"
```

### Alembic Migration

**File:** `apps/synapse/backend/alembic/versions/xxx_add_workflow_events.py`

```python
"""Add workflow events and execution snapshots tables

Revision ID: xxx
Revises: previous_revision
Create Date: 2025-11-28
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision = 'xxx'
down_revision = 'previous_revision'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create workflow_events table
    op.create_table(
        'workflow_events',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('aggregate_type', sa.String(30), nullable=False),
        sa.Column('aggregate_id', sa.String(100), nullable=True),
        sa.Column('project_id', sa.String(), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('rule_id', sa.String(), sa.ForeignKey('rule_definitions.id'), nullable=True),
        sa.Column('discipline', sa.String(30), nullable=True),
        sa.Column('payload', JSONB, nullable=False, server_default='{}'),
        sa.Column('metadata', JSONB, nullable=True, server_default='{}'),
        sa.Column('correlation_id', UUID(as_uuid=True), nullable=False),
        sa.Column('causation_id', UUID(as_uuid=True), nullable=True),
        sa.Column('sequence_num', sa.BigInteger(), nullable=False, server_default='0'),
        sa.Column('user_id', sa.String(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('is_rolled_back', sa.Boolean(), nullable=False, server_default='false'),
    )

    # Create indexes
    op.create_index('ix_workflow_events_event_type', 'workflow_events', ['event_type'])
    op.create_index('ix_workflow_events_aggregate_type', 'workflow_events', ['aggregate_type'])
    op.create_index('ix_workflow_events_aggregate_id', 'workflow_events', ['aggregate_id'])
    op.create_index('ix_workflow_events_project_id', 'workflow_events', ['project_id'])
    op.create_index('ix_workflow_events_rule_id', 'workflow_events', ['rule_id'])
    op.create_index('ix_workflow_events_discipline', 'workflow_events', ['discipline'])
    op.create_index('ix_workflow_events_correlation_id', 'workflow_events', ['correlation_id'])
    op.create_index('ix_workflow_events_timestamp', 'workflow_events', ['timestamp'])
    op.create_index('ix_workflow_events_project_time', 'workflow_events', ['project_id', 'timestamp'])
    op.create_index('ix_workflow_events_aggregate_lookup', 'workflow_events', ['aggregate_type', 'aggregate_id', 'timestamp'])
    op.create_index('ix_workflow_events_correlation_seq', 'workflow_events', ['correlation_id', 'sequence_num'])

    # Create execution_snapshots table
    op.create_table(
        'execution_snapshots',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('correlation_id', UUID(as_uuid=True), unique=True, nullable=False),
        sa.Column('project_id', sa.String(), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('snapshot_data', JSONB, nullable=False),
        sa.Column('events_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('status', sa.String(20), nullable=False, server_default='ACTIVE'),
        sa.Column('executed_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('rolled_back_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('rolled_back_by', sa.String(), sa.ForeignKey('users.id'), nullable=True),
    )

    op.create_index('ix_execution_snapshots_correlation_id', 'execution_snapshots', ['correlation_id'])
    op.create_index('ix_execution_snapshots_project_id', 'execution_snapshots', ['project_id'])
    op.create_index('ix_execution_snapshots_status', 'execution_snapshots', ['status'])


def downgrade() -> None:
    op.drop_table('execution_snapshots')
    op.drop_table('workflow_events')
```

---

## Backend Services

### EventStore Service

**File:** `apps/synapse/backend/app/services/event_store.py`

```python
"""
Event Store Service

Provides append-only event storage and querying capabilities.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.models.workflow_events import (
    WorkflowEvent, WorkflowEventType, AggregateType,
    ExecutionSnapshot, SnapshotStatus
)


class EventStore:
    """
    Immutable event store for workflow events.

    All events are append-only. Events are never modified or deleted.
    """

    def __init__(self, db: Session, project_id: str, user_id: Optional[str] = None):
        self.db = db
        self.project_id = project_id
        self.user_id = user_id
        self._correlation_id: Optional[uuid.UUID] = None
        self._sequence_counter: int = 0

    def start_batch(self) -> uuid.UUID:
        """Start a new event batch, returns correlation_id"""
        self._correlation_id = uuid.uuid4()
        self._sequence_counter = 0
        return self._correlation_id

    @property
    def correlation_id(self) -> Optional[uuid.UUID]:
        return self._correlation_id

    def emit(
        self,
        event_type: WorkflowEventType,
        aggregate_type: AggregateType,
        aggregate_id: Optional[str] = None,
        payload: Optional[dict] = None,
        rule_id: Optional[str] = None,
        discipline: Optional[str] = None,
        causation_id: Optional[uuid.UUID] = None,
        metadata: Optional[dict] = None,
    ) -> WorkflowEvent:
        """
        Emit a new event to the store.

        Args:
            event_type: Type of event
            aggregate_type: Type of entity being affected
            aggregate_id: ID of the entity
            payload: Event data (before/after state, diff)
            rule_id: Rule that caused this event (if applicable)
            discipline: Engineering discipline
            causation_id: ID of event that caused this one
            metadata: Additional metadata

        Returns:
            Created WorkflowEvent
        """
        if not self._correlation_id:
            self.start_batch()

        event = WorkflowEvent(
            event_type=event_type,
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            project_id=self.project_id,
            rule_id=rule_id,
            discipline=discipline,
            payload=payload or {},
            metadata=metadata or {},
            correlation_id=self._correlation_id,
            causation_id=causation_id,
            sequence_num=self._sequence_counter,
            user_id=self.user_id,
        )

        self.db.add(event)
        self._sequence_counter += 1

        return event

    def query(
        self,
        event_types: Optional[list[WorkflowEventType]] = None,
        aggregate_types: Optional[list[AggregateType]] = None,
        aggregate_id: Optional[str] = None,
        rule_id: Optional[str] = None,
        discipline: Optional[str] = None,
        correlation_id: Optional[uuid.UUID] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        include_rolled_back: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[WorkflowEvent], int]:
        """
        Query events with filters.

        Returns:
            Tuple of (events, total_count)
        """
        query = self.db.query(WorkflowEvent).filter(
            WorkflowEvent.project_id == self.project_id
        )

        if not include_rolled_back:
            query = query.filter(WorkflowEvent.is_rolled_back == False)

        if event_types:
            query = query.filter(WorkflowEvent.event_type.in_(event_types))

        if aggregate_types:
            query = query.filter(WorkflowEvent.aggregate_type.in_(aggregate_types))

        if aggregate_id:
            query = query.filter(WorkflowEvent.aggregate_id == aggregate_id)

        if rule_id:
            query = query.filter(WorkflowEvent.rule_id == rule_id)

        if discipline:
            query = query.filter(WorkflowEvent.discipline == discipline)

        if correlation_id:
            query = query.filter(WorkflowEvent.correlation_id == correlation_id)

        if from_date:
            query = query.filter(WorkflowEvent.timestamp >= from_date)

        if to_date:
            query = query.filter(WorkflowEvent.timestamp <= to_date)

        total = query.count()

        events = (
            query
            .order_by(WorkflowEvent.timestamp.desc(), WorkflowEvent.sequence_num.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        return events, total

    def get_by_correlation(self, correlation_id: uuid.UUID) -> list[WorkflowEvent]:
        """Get all events for a correlation ID, ordered by sequence"""
        return (
            self.db.query(WorkflowEvent)
            .filter(
                WorkflowEvent.project_id == self.project_id,
                WorkflowEvent.correlation_id == correlation_id
            )
            .order_by(WorkflowEvent.sequence_num)
            .all()
        )

    def get_asset_history(self, asset_id: str) -> list[WorkflowEvent]:
        """Get all events for a specific asset"""
        return (
            self.db.query(WorkflowEvent)
            .filter(
                WorkflowEvent.project_id == self.project_id,
                WorkflowEvent.aggregate_type == AggregateType.ASSET,
                WorkflowEvent.aggregate_id == asset_id,
                WorkflowEvent.is_rolled_back == False
            )
            .order_by(WorkflowEvent.timestamp)
            .all()
        )


class SnapshotService:
    """
    Manages execution snapshots for rollback capability.
    """

    def __init__(self, db: Session, project_id: str):
        self.db = db
        self.project_id = project_id

    def create_snapshot(
        self,
        correlation_id: uuid.UUID,
        entities: dict,
    ) -> ExecutionSnapshot:
        """
        Create a pre-execution snapshot.

        Args:
            correlation_id: Batch correlation ID
            entities: Dict with 'assets', 'cables', 'edges' lists

        Returns:
            Created ExecutionSnapshot
        """
        snapshot = ExecutionSnapshot(
            correlation_id=correlation_id,
            project_id=self.project_id,
            snapshot_data=entities,
        )

        self.db.add(snapshot)
        self.db.commit()

        return snapshot

    def update_event_count(self, correlation_id: uuid.UUID, count: int):
        """Update the event count for a snapshot"""
        snapshot = self.get_by_correlation(correlation_id)
        if snapshot:
            snapshot.events_count = count
            self.db.commit()

    def get_by_correlation(self, correlation_id: uuid.UUID) -> Optional[ExecutionSnapshot]:
        """Get snapshot by correlation ID"""
        return (
            self.db.query(ExecutionSnapshot)
            .filter(
                ExecutionSnapshot.project_id == self.project_id,
                ExecutionSnapshot.correlation_id == correlation_id
            )
            .first()
        )

    def mark_rolled_back(
        self,
        correlation_id: uuid.UUID,
        user_id: Optional[str] = None
    ) -> Optional[ExecutionSnapshot]:
        """Mark a snapshot as rolled back"""
        snapshot = self.get_by_correlation(correlation_id)
        if snapshot:
            snapshot.status = SnapshotStatus.ROLLED_BACK
            snapshot.rolled_back_at = datetime.utcnow()
            snapshot.rolled_back_by = user_id
            self.db.commit()
        return snapshot

    def list_active(self, limit: int = 50) -> list[ExecutionSnapshot]:
        """List active (non-rolled-back) snapshots"""
        return (
            self.db.query(ExecutionSnapshot)
            .filter(
                ExecutionSnapshot.project_id == self.project_id,
                ExecutionSnapshot.status == SnapshotStatus.ACTIVE
            )
            .order_by(ExecutionSnapshot.executed_at.desc())
            .limit(limit)
            .all()
        )
```

### RollbackService

**File:** `apps/synapse/backend/app/services/rollback_service.py`

```python
"""
Rollback Service

Handles reverting batch executions using snapshots.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models.models import Asset
from app.models.cables import Cable
from app.models.metamodel import MetamodelEdge
from app.models.workflow_events import (
    WorkflowEvent, WorkflowEventType, AggregateType,
    ExecutionSnapshot, SnapshotStatus
)
from app.services.event_store import EventStore, SnapshotService


class RollbackService:
    """
    Handles rollback of batch executions.

    Uses snapshots to restore previous state and marks events as rolled back.
    """

    def __init__(self, db: Session, project_id: str, user_id: Optional[str] = None):
        self.db = db
        self.project_id = project_id
        self.user_id = user_id
        self.event_store = EventStore(db, project_id, user_id)
        self.snapshot_service = SnapshotService(db, project_id)

    def rollback(self, correlation_id: uuid.UUID) -> dict:
        """
        Rollback a batch execution.

        Args:
            correlation_id: The batch to rollback

        Returns:
            Summary of rollback actions
        """
        # 1. Get snapshot
        snapshot = self.snapshot_service.get_by_correlation(correlation_id)
        if not snapshot:
            raise ValueError(f"No snapshot found for correlation_id: {correlation_id}")

        if snapshot.status == SnapshotStatus.ROLLED_BACK:
            raise ValueError(f"Batch {correlation_id} has already been rolled back")

        # 2. Get all events in this batch
        events = self.event_store.get_by_correlation(correlation_id)

        # 3. Start rollback batch
        rollback_correlation = self.event_store.start_batch()

        # 4. Process events in reverse order
        deleted_assets = []
        deleted_cables = []
        deleted_edges = []
        restored_assets = []

        for event in reversed(events):
            if event.event_type == WorkflowEventType.ASSET_CREATED:
                # Delete created asset
                asset = self.db.query(Asset).filter(
                    Asset.id == event.aggregate_id
                ).first()
                if asset:
                    self.db.delete(asset)
                    deleted_assets.append(event.aggregate_id)

            elif event.event_type == WorkflowEventType.CABLE_CREATED:
                # Delete created cable
                cable = self.db.query(Cable).filter(
                    Cable.id == event.aggregate_id
                ).first()
                if cable:
                    self.db.delete(cable)
                    deleted_cables.append(event.aggregate_id)

            elif event.event_type == WorkflowEventType.RELATIONSHIP_CREATED:
                # Delete created edge
                edge = self.db.query(MetamodelEdge).filter(
                    MetamodelEdge.id == event.aggregate_id
                ).first()
                if edge:
                    self.db.delete(edge)
                    deleted_edges.append(event.aggregate_id)

            elif event.event_type == WorkflowEventType.ASSET_UPDATED:
                # Restore previous state
                if event.payload.get("before"):
                    asset = self.db.query(Asset).filter(
                        Asset.id == event.aggregate_id
                    ).first()
                    if asset:
                        before = event.payload["before"]
                        asset.properties = before.get("properties", asset.properties)
                        restored_assets.append(event.aggregate_id)

            # Mark event as rolled back
            event.is_rolled_back = True

        # 5. Emit rollback event
        self.event_store.emit(
            event_type=WorkflowEventType.BATCH_ROLLED_BACK,
            aggregate_type=AggregateType.BATCH,
            aggregate_id=str(correlation_id),
            payload={
                "original_correlation_id": str(correlation_id),
                "deleted_assets": deleted_assets,
                "deleted_cables": deleted_cables,
                "deleted_edges": deleted_edges,
                "restored_assets": restored_assets,
            }
        )

        # 6. Mark snapshot as rolled back
        self.snapshot_service.mark_rolled_back(correlation_id, self.user_id)

        # 7. Commit
        self.db.commit()

        return {
            "status": "rolled_back",
            "correlation_id": str(correlation_id),
            "rollback_correlation_id": str(rollback_correlation),
            "rolled_back_events": len(events),
            "summary": {
                "assets_deleted": len(deleted_assets),
                "cables_deleted": len(deleted_cables),
                "edges_deleted": len(deleted_edges),
                "assets_restored": len(restored_assets),
            }
        }
```

---

## API Endpoints

### Rules Execution Router

**File:** `apps/synapse/backend/app/api/endpoints/rule_execution.py`

```python
"""
Rule Execution API Endpoints

Endpoints for executing rules with filters, dry run, and real-time updates.
"""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.services.rule_engine import RuleEngine
from app.services.event_store import EventStore
from app.services.rollback_service import RollbackService

router = APIRouter(prefix="/rules", tags=["Rule Execution"])


# Schemas
class ExecutionFilters(BaseModel):
    rule_ids: Optional[list[str]] = None
    disciplines: Optional[list[str]] = None
    action_types: Optional[list[str]] = None
    asset_ids: Optional[list[str]] = None
    asset_types: Optional[list[str]] = None


class ExecuteRulesRequest(BaseModel):
    project_id: str
    mode: str = "execute"  # "execute" or "dry_run"
    filters: Optional[ExecutionFilters] = None


class ExecuteRulesResponse(BaseModel):
    execution_id: str
    correlation_id: str
    ws_url: str
    status: str


class RollbackRequest(BaseModel):
    correlation_id: str


# Endpoints
@router.post("/execute", response_model=ExecuteRulesResponse)
async def execute_rules(
    request: ExecuteRulesRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Execute rules with optional filters.

    Modes:
    - execute: Apply rules and persist changes
    - dry_run: Preview changes without persisting

    Returns WebSocket URL for real-time updates.
    """
    execution_id = str(uuid.uuid4())

    # Store execution context for WebSocket
    # (In production, use Redis or similar)
    execution_context = {
        "project_id": request.project_id,
        "mode": request.mode,
        "filters": request.filters.dict() if request.filters else None,
        "user_id": current_user.id,
    }

    # Start execution in background (or return preview for dry_run)
    event_store = EventStore(db, request.project_id, current_user.id)
    correlation_id = event_store.start_batch()

    return ExecuteRulesResponse(
        execution_id=execution_id,
        correlation_id=str(correlation_id),
        ws_url=f"/ws/execution/{execution_id}",
        status="started" if request.mode == "execute" else "preview",
    )


@router.post("/rollback")
async def rollback_execution(
    request: RollbackRequest,
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Rollback a batch execution.

    Restores state from snapshot and marks events as rolled back.
    """
    try:
        correlation_id = uuid.UUID(request.correlation_id)
    except ValueError:
        raise HTTPException(400, "Invalid correlation_id format")

    rollback_service = RollbackService(db, project_id, current_user.id)

    try:
        result = rollback_service.rollback(correlation_id)
        return result
    except ValueError as e:
        raise HTTPException(400, str(e))
```

### Events Timeline Router

**File:** `apps/synapse/backend/app/api/endpoints/events.py`

```python
"""
Events Timeline API Endpoints

Query workflow events with multi-criteria filtering.
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.workflow_events import WorkflowEventType, AggregateType
from app.services.event_store import EventStore

router = APIRouter(prefix="/events", tags=["Events"])


class EventResponse(BaseModel):
    id: str
    event_type: str
    aggregate_type: str
    aggregate_id: Optional[str]
    payload: dict
    rule_id: Optional[str]
    discipline: Optional[str]
    correlation_id: str
    timestamp: datetime
    is_rolled_back: bool

    class Config:
        from_attributes = True


class TimelineResponse(BaseModel):
    events: list[EventResponse]
    total: int
    page: int
    pages: int


@router.get("/timeline", response_model=TimelineResponse)
async def get_timeline(
    project_id: str,
    asset_id: Optional[str] = None,
    rule_id: Optional[str] = None,
    discipline: Optional[str] = None,
    event_types: Optional[str] = Query(None, description="Comma-separated event types"),
    correlation_id: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    page: int = 1,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Query workflow events with filters.

    Supports filtering by:
    - asset_id: Events for a specific asset
    - rule_id: Events from a specific rule
    - discipline: Events for a discipline (ELECTRICAL, AUTOMATION, etc.)
    - event_types: Comma-separated list (ASSET_CREATED,CABLE_CREATED)
    - correlation_id: Events from a specific batch
    - from_date/to_date: Date range
    """
    event_store = EventStore(db, project_id)

    # Parse event types
    parsed_event_types = None
    if event_types:
        parsed_event_types = [
            WorkflowEventType(t.strip())
            for t in event_types.split(",")
        ]

    # Determine aggregate type and ID
    aggregate_types = None
    aggregate_id_filter = None
    if asset_id:
        aggregate_types = [AggregateType.ASSET]
        aggregate_id_filter = asset_id

    events, total = event_store.query(
        event_types=parsed_event_types,
        aggregate_types=aggregate_types,
        aggregate_id=aggregate_id_filter,
        rule_id=rule_id,
        discipline=discipline,
        from_date=from_date,
        to_date=to_date,
        limit=limit,
        offset=(page - 1) * limit,
    )

    return TimelineResponse(
        events=[
            EventResponse(
                id=str(e.id),
                event_type=e.event_type.value,
                aggregate_type=e.aggregate_type.value,
                aggregate_id=e.aggregate_id,
                payload=e.payload,
                rule_id=e.rule_id,
                discipline=e.discipline,
                correlation_id=str(e.correlation_id),
                timestamp=e.timestamp,
                is_rolled_back=e.is_rolled_back,
            )
            for e in events
        ],
        total=total,
        page=page,
        pages=(total + limit - 1) // limit,
    )


@router.get("/assets/{asset_id}/history")
async def get_asset_history(
    asset_id: str,
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get complete history for a specific asset.

    Returns all events related to the asset in chronological order.
    """
    event_store = EventStore(db, project_id)
    events = event_store.get_asset_history(asset_id)

    return {
        "asset_id": asset_id,
        "history": [e.to_dict() for e in events],
        "total_events": len(events),
    }
```

---

## WebSocket Protocol

### WebSocket Handler

**File:** `apps/synapse/backend/app/api/websocket/execution.py`

```python
"""
WebSocket handler for real-time rule execution updates.
"""

import asyncio
import json
from typing import Optional

from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session


class ExecutionWebSocket:
    """
    Manages WebSocket connections for rule execution updates.
    """

    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, execution_id: str):
        """Accept and store connection"""
        await websocket.accept()
        self.active_connections[execution_id] = websocket

    def disconnect(self, execution_id: str):
        """Remove connection"""
        self.active_connections.pop(execution_id, None)

    async def send_message(self, execution_id: str, message: dict):
        """Send message to specific execution"""
        websocket = self.active_connections.get(execution_id)
        if websocket:
            await websocket.send_json(message)

    async def broadcast_progress(
        self,
        execution_id: str,
        message_type: str,
        data: dict
    ):
        """Send progress update"""
        await self.send_message(execution_id, {
            "type": message_type,
            **data
        })


# Singleton instance
execution_ws = ExecutionWebSocket()


# Message types
class WSMessageType:
    STARTED = "STARTED"
    RULE_START = "RULE_START"
    RULE_COMPLETE = "RULE_COMPLETE"
    ACTION = "ACTION"
    PROGRESS = "PROGRESS"
    ERROR = "ERROR"
    COMPLETED = "COMPLETED"


# WebSocket route handler
async def execution_websocket_handler(
    websocket: WebSocket,
    execution_id: str,
):
    """
    WebSocket endpoint for execution updates.

    Message format:
    {
        "type": "STARTED" | "RULE_START" | "ACTION" | "PROGRESS" | "COMPLETED" | "ERROR",
        ...data
    }
    """
    await execution_ws.connect(websocket, execution_id)

    try:
        # Keep connection alive and listen for client messages
        while True:
            try:
                # Wait for client ping or close
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=30.0
                )
                # Handle client messages if needed (e.g., cancel)
                if data == "ping":
                    await websocket.send_text("pong")
            except asyncio.TimeoutError:
                # Send keepalive
                await websocket.send_text("ping")
    except WebSocketDisconnect:
        execution_ws.disconnect(execution_id)
```

### WebSocket Message Examples

```typescript
// Connection
const ws = new WebSocket(`ws://localhost:8001/ws/execution/${executionId}`);

// Message: Execution Started
{
  "type": "STARTED",
  "execution_id": "exec-xxx",
  "correlation_id": "corr-xxx",
  "total_rules": 15,
  "total_assets": 100,
  "filters_applied": {
    "disciplines": ["ELECTRICAL"],
    "rule_ids": null
  }
}

// Message: Rule Starting
{
  "type": "RULE_START",
  "rule_id": "rule-xxx",
  "rule_name": "Create Motor for Pumps",
  "discipline": "ELECTRICAL",
  "assets_to_process": 25,
  "progress": 10
}

// Message: Individual Action
{
  "type": "ACTION",
  "rule_id": "rule-xxx",
  "asset_id": "asset-xxx",
  "asset_tag": "P-101",
  "action": "CREATED",
  "result": {
    "created_id": "asset-yyy",
    "created_tag": "P-101-M",
    "created_type": "MOTOR"
  }
}

// Message: Progress Update
{
  "type": "PROGRESS",
  "progress": 65,
  "rules_completed": 10,
  "rules_total": 15,
  "actions_completed": 45,
  "errors": 0
}

// Message: Rule Completed
{
  "type": "RULE_COMPLETE",
  "rule_id": "rule-xxx",
  "rule_name": "Create Motor for Pumps",
  "assets_processed": 25,
  "actions_taken": 20,
  "skipped": 5,
  "errors": 0
}

// Message: Execution Completed
{
  "type": "COMPLETED",
  "execution_id": "exec-xxx",
  "correlation_id": "corr-xxx",
  "duration_ms": 5234,
  "summary": {
    "rules_executed": 15,
    "assets_processed": 100,
    "actions_taken": 75,
    "skipped": 25,
    "errors": 0,
    "created": {
      "assets": 20,
      "cables": 15,
      "edges": 20
    }
  }
}

// Message: Error
{
  "type": "ERROR",
  "rule_id": "rule-xxx",
  "asset_id": "asset-xxx",
  "message": "Failed to create motor: duplicate tag",
  "recoverable": true
}
```

---

## Frontend Components

### useExecutionSocket Hook

**File:** `apps/synapse/frontend/src/hooks/useExecutionSocket.ts`

```typescript
import { useState, useEffect, useCallback, useRef } from 'react';

interface ExecutionProgress {
  status: 'idle' | 'connecting' | 'running' | 'completed' | 'error';
  progress: number;
  totalRules: number;
  totalAssets: number;
  rulesCompleted: number;
  actionsCompleted: number;
  errors: number;
  currentRule?: {
    id: string;
    name: string;
    progress: number;
  };
  actions: ExecutionAction[];
  summary?: ExecutionSummary;
}

interface ExecutionAction {
  timestamp: Date;
  ruleId: string;
  assetId: string;
  assetTag: string;
  action: string;
  result?: {
    createdId?: string;
    createdTag?: string;
    createdType?: string;
  };
}

interface ExecutionSummary {
  rulesExecuted: number;
  assetsProcessed: number;
  actionsTaken: number;
  skipped: number;
  errors: number;
  created: {
    assets: number;
    cables: number;
    edges: number;
  };
  durationMs: number;
}

export function useExecutionSocket(executionId: string | null) {
  const wsRef = useRef<WebSocket | null>(null);
  const [progress, setProgress] = useState<ExecutionProgress>({
    status: 'idle',
    progress: 0,
    totalRules: 0,
    totalAssets: 0,
    rulesCompleted: 0,
    actionsCompleted: 0,
    errors: 0,
    actions: [],
  });

  const connect = useCallback(() => {
    if (!executionId) return;

    setProgress(prev => ({ ...prev, status: 'connecting' }));

    const ws = new WebSocket(
      `${import.meta.env.VITE_WS_URL}/ws/execution/${executionId}`
    );

    ws.onopen = () => {
      setProgress(prev => ({ ...prev, status: 'running' }));
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);

      switch (message.type) {
        case 'STARTED':
          setProgress(prev => ({
            ...prev,
            status: 'running',
            totalRules: message.total_rules,
            totalAssets: message.total_assets,
          }));
          break;

        case 'RULE_START':
          setProgress(prev => ({
            ...prev,
            currentRule: {
              id: message.rule_id,
              name: message.rule_name,
              progress: 0,
            },
            progress: message.progress,
          }));
          break;

        case 'ACTION':
          setProgress(prev => ({
            ...prev,
            actionsCompleted: prev.actionsCompleted + 1,
            actions: [
              {
                timestamp: new Date(),
                ruleId: message.rule_id,
                assetId: message.asset_id,
                assetTag: message.asset_tag,
                action: message.action,
                result: message.result,
              },
              ...prev.actions.slice(0, 99), // Keep last 100
            ],
          }));
          break;

        case 'PROGRESS':
          setProgress(prev => ({
            ...prev,
            progress: message.progress,
            rulesCompleted: message.rules_completed,
            actionsCompleted: message.actions_completed,
            errors: message.errors,
          }));
          break;

        case 'COMPLETED':
          setProgress(prev => ({
            ...prev,
            status: 'completed',
            progress: 100,
            summary: {
              rulesExecuted: message.summary.rules_executed,
              assetsProcessed: message.summary.assets_processed,
              actionsTaken: message.summary.actions_taken,
              skipped: message.summary.skipped,
              errors: message.summary.errors,
              created: message.summary.created,
              durationMs: message.duration_ms,
            },
          }));
          break;

        case 'ERROR':
          setProgress(prev => ({
            ...prev,
            errors: prev.errors + 1,
          }));
          break;
      }
    };

    ws.onerror = () => {
      setProgress(prev => ({ ...prev, status: 'error' }));
    };

    ws.onclose = () => {
      if (progress.status === 'running') {
        setProgress(prev => ({ ...prev, status: 'error' }));
      }
    };

    wsRef.current = ws;
  }, [executionId]);

  const disconnect = useCallback(() => {
    wsRef.current?.close();
    wsRef.current = null;
  }, []);

  const reset = useCallback(() => {
    setProgress({
      status: 'idle',
      progress: 0,
      totalRules: 0,
      totalAssets: 0,
      rulesCompleted: 0,
      actionsCompleted: 0,
      errors: 0,
      actions: [],
    });
  }, []);

  useEffect(() => {
    if (executionId) {
      connect();
    }
    return () => disconnect();
  }, [executionId, connect, disconnect]);

  return {
    progress,
    connect,
    disconnect,
    reset,
    isConnected: wsRef.current?.readyState === WebSocket.OPEN,
  };
}
```

---

## Testing Strategy

### Backend Tests

**File:** `apps/synapse/backend/tests/test_event_store.py`

```python
"""Tests for EventStore service"""

import pytest
import uuid
from datetime import datetime, timedelta

from app.models.workflow_events import WorkflowEventType, AggregateType
from app.services.event_store import EventStore, SnapshotService


class TestEventStore:

    def test_emit_creates_event(self, db_session, test_project):
        """Test that emit creates an event with correct data"""
        store = EventStore(db_session, test_project.id)
        store.start_batch()

        event = store.emit(
            event_type=WorkflowEventType.ASSET_CREATED,
            aggregate_type=AggregateType.ASSET,
            aggregate_id="asset-123",
            payload={"tag": "P-101", "type": "PUMP"},
            discipline="ELECTRICAL",
        )

        assert event.id is not None
        assert event.event_type == WorkflowEventType.ASSET_CREATED
        assert event.aggregate_id == "asset-123"
        assert event.payload["tag"] == "P-101"

    def test_batch_correlation(self, db_session, test_project):
        """Test that events in same batch share correlation_id"""
        store = EventStore(db_session, test_project.id)
        correlation_id = store.start_batch()

        event1 = store.emit(
            WorkflowEventType.ASSET_CREATED,
            AggregateType.ASSET,
            "asset-1"
        )
        event2 = store.emit(
            WorkflowEventType.ASSET_CREATED,
            AggregateType.ASSET,
            "asset-2"
        )

        assert event1.correlation_id == correlation_id
        assert event2.correlation_id == correlation_id
        assert event1.sequence_num < event2.sequence_num

    def test_query_by_filters(self, db_session, test_project):
        """Test querying events with multiple filters"""
        store = EventStore(db_session, test_project.id)
        store.start_batch()

        # Create events
        store.emit(
            WorkflowEventType.ASSET_CREATED,
            AggregateType.ASSET,
            "asset-1",
            discipline="ELECTRICAL"
        )
        store.emit(
            WorkflowEventType.CABLE_CREATED,
            AggregateType.CABLE,
            "cable-1",
            discipline="ELECTRICAL"
        )
        store.emit(
            WorkflowEventType.ASSET_CREATED,
            AggregateType.ASSET,
            "asset-2",
            discipline="AUTOMATION"
        )
        db_session.commit()

        # Query by discipline
        events, total = store.query(discipline="ELECTRICAL")
        assert total == 2

        # Query by event type
        events, total = store.query(
            event_types=[WorkflowEventType.ASSET_CREATED]
        )
        assert total == 2

    def test_get_asset_history(self, db_session, test_project):
        """Test getting complete history for an asset"""
        store = EventStore(db_session, test_project.id)

        # Simulate asset lifecycle
        store.start_batch()
        store.emit(
            WorkflowEventType.ASSET_CREATED,
            AggregateType.ASSET,
            "asset-test",
            payload={"tag": "P-101"}
        )
        db_session.commit()

        store.start_batch()
        store.emit(
            WorkflowEventType.ASSET_UPDATED,
            AggregateType.ASSET,
            "asset-test",
            payload={"before": {"hp": None}, "after": {"hp": 50}}
        )
        db_session.commit()

        history = store.get_asset_history("asset-test")
        assert len(history) == 2
        assert history[0].event_type == WorkflowEventType.ASSET_CREATED
        assert history[1].event_type == WorkflowEventType.ASSET_UPDATED


class TestSnapshotService:

    def test_create_and_retrieve_snapshot(self, db_session, test_project):
        """Test creating and retrieving a snapshot"""
        service = SnapshotService(db_session, test_project.id)
        correlation_id = uuid.uuid4()

        snapshot = service.create_snapshot(
            correlation_id=correlation_id,
            entities={
                "assets": [{"id": "1", "tag": "P-101"}],
                "cables": [],
                "edges": []
            }
        )

        retrieved = service.get_by_correlation(correlation_id)
        assert retrieved is not None
        assert retrieved.snapshot_data["assets"][0]["tag"] == "P-101"

    def test_mark_rolled_back(self, db_session, test_project):
        """Test marking snapshot as rolled back"""
        service = SnapshotService(db_session, test_project.id)
        correlation_id = uuid.uuid4()

        service.create_snapshot(correlation_id, {"assets": []})
        service.mark_rolled_back(correlation_id, "user-123")

        snapshot = service.get_by_correlation(correlation_id)
        assert snapshot.status.value == "ROLLED_BACK"
        assert snapshot.rolled_back_by == "user-123"
```

### Frontend Tests

**File:** `apps/synapse/frontend/src/hooks/useExecutionSocket.test.ts`

```typescript
import { renderHook, act } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import { useExecutionSocket } from './useExecutionSocket';

// Mock WebSocket
class MockWebSocket {
  static instances: MockWebSocket[] = [];
  onopen: (() => void) | null = null;
  onmessage: ((e: { data: string }) => void) | null = null;
  onclose: (() => void) | null = null;
  onerror: (() => void) | null = null;
  readyState = WebSocket.CONNECTING;

  constructor(public url: string) {
    MockWebSocket.instances.push(this);
    setTimeout(() => {
      this.readyState = WebSocket.OPEN;
      this.onopen?.();
    }, 0);
  }

  close() {
    this.readyState = WebSocket.CLOSED;
    this.onclose?.();
  }

  simulateMessage(data: object) {
    this.onmessage?.({ data: JSON.stringify(data) });
  }
}

describe('useExecutionSocket', () => {
  beforeEach(() => {
    MockWebSocket.instances = [];
    vi.stubGlobal('WebSocket', MockWebSocket);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('connects when executionId is provided', async () => {
    const { result } = renderHook(() =>
      useExecutionSocket('exec-123')
    );

    await vi.waitFor(() => {
      expect(result.current.progress.status).toBe('running');
    });
  });

  it('updates progress on STARTED message', async () => {
    const { result } = renderHook(() =>
      useExecutionSocket('exec-123')
    );

    await vi.waitFor(() => {
      expect(MockWebSocket.instances.length).toBe(1);
    });

    act(() => {
      MockWebSocket.instances[0].simulateMessage({
        type: 'STARTED',
        total_rules: 10,
        total_assets: 50,
      });
    });

    expect(result.current.progress.totalRules).toBe(10);
    expect(result.current.progress.totalAssets).toBe(50);
  });

  it('accumulates actions', async () => {
    const { result } = renderHook(() =>
      useExecutionSocket('exec-123')
    );

    await vi.waitFor(() => {
      expect(MockWebSocket.instances.length).toBe(1);
    });

    act(() => {
      MockWebSocket.instances[0].simulateMessage({
        type: 'ACTION',
        rule_id: 'rule-1',
        asset_id: 'asset-1',
        asset_tag: 'P-101',
        action: 'CREATED',
        result: { createdTag: 'P-101-M' },
      });
    });

    expect(result.current.progress.actions.length).toBe(1);
    expect(result.current.progress.actionsCompleted).toBe(1);
  });

  it('sets completed status on COMPLETED message', async () => {
    const { result } = renderHook(() =>
      useExecutionSocket('exec-123')
    );

    await vi.waitFor(() => {
      expect(MockWebSocket.instances.length).toBe(1);
    });

    act(() => {
      MockWebSocket.instances[0].simulateMessage({
        type: 'COMPLETED',
        duration_ms: 5000,
        summary: {
          rules_executed: 10,
          assets_processed: 50,
          actions_taken: 30,
          skipped: 20,
          errors: 0,
          created: { assets: 15, cables: 10, edges: 15 },
        },
      });
    });

    expect(result.current.progress.status).toBe('completed');
    expect(result.current.progress.summary?.actionsTaken).toBe(30);
  });
});
```

---

## File Structure Summary

```
apps/synapse/
├── backend/
│   ├── app/
│   │   ├── models/
│   │   │   └── workflow_events.py          # NEW: Event models
│   │   ├── services/
│   │   │   ├── event_store.py              # NEW: EventStore service
│   │   │   ├── rollback_service.py         # NEW: Rollback service
│   │   │   └── rule_engine.py              # MODIFY: Add event emission
│   │   └── api/
│   │       ├── endpoints/
│   │       │   ├── rule_execution.py       # NEW: Execute/rollback endpoints
│   │       │   └── events.py               # NEW: Timeline/history endpoints
│   │       └── websocket/
│   │           └── execution.py            # NEW: WebSocket handler
│   ├── alembic/
│   │   └── versions/
│   │       └── xxx_add_workflow_events.py  # NEW: Migration
│   └── tests/
│       ├── test_event_store.py             # NEW: EventStore tests
│       ├── test_rollback.py                # NEW: Rollback tests
│       └── test_events_api.py              # NEW: API tests
│
└── frontend/
    └── src/
        ├── hooks/
        │   └── useExecutionSocket.ts       # NEW: WebSocket hook
        ├── components/
        │   └── rules/
        │       ├── RuleExecutionPanel.tsx  # NEW: Execution UI
        │       ├── WorkflowTimeline.tsx    # NEW: Timeline UI
        │       └── AssetHistoryPanel.tsx   # NEW: History UI
        └── services/
            └── ruleExecutionApi.ts         # NEW: API client
```

---

**Next:** See [API Reference](../reference/rule-engine-api.md) for complete endpoint documentation.
