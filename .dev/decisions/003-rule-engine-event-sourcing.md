# ADR-003: Rule Engine Event Sourcing Architecture

**Status:** Accepted
**Date:** 2025-11-28
**Authors:** Development Team
**Whiteboard Session:** #4 - Rule Engine

---

## Context

The SYNAPSE Rule Engine needs to provide:
1. **Complete traceability** - Engineers must understand what happened, when, and why
2. **Real-time feedback** - Users should see rule execution progress live
3. **Rollback capability** - Undo batch executions when mistakes are detected
4. **Multi-criteria filtering** - Query events by asset, rule, discipline, date range
5. **Audit compliance** - Full audit trail for engineering changes

The current implementation (`RuleExecution` table) logs executions but lacks:
- Immutable event history (records can be modified)
- Rollback support
- Real-time streaming
- Rich filtering capabilities
- Before/after snapshots

---

## Decision

We will implement an **Event Sourcing** architecture with:

### 1. Immutable Event Store (`workflow_events`)

All changes are recorded as immutable events. The event store becomes the source of truth for what happened.

```
workflow_events (append-only)
├── Event identification (id, event_type, aggregate_type, aggregate_id)
├── Context (project_id, rule_id, discipline)
├── Payload (before state, after state, diff)
├── Correlation (correlation_id, causation_id, sequence_num)
├── Metadata (user_id, timestamp, is_rolledback)
```

### 2. Execution Snapshots for Rollback

Before each batch execution, capture a snapshot of affected entities. This enables precise rollback.

```
execution_snapshots
├── correlation_id (links to event batch)
├── snapshot_data (JSON of assets, cables, edges before execution)
├── status (ACTIVE, ROLLED_BACK)
```

### 3. Real-time WebSocket Pipeline

Stream execution progress to frontend via WebSocket:
- Execution started (total rules, total assets)
- Rule progress (which rule, percentage)
- Individual actions (asset created, cable sized)
- Execution completed (summary, correlation_id)

### 4. Multi-criteria Query API

RESTful endpoints with comprehensive filtering:
- By asset (single asset history)
- By rule (rule execution history)
- By discipline (ELECTRICAL, AUTOMATION, etc.)
- By event type (CREATED, UPDATED, etc.)
- By date range
- Combined filters

---

## Architecture

### Event Types

```python
class WorkflowEventType(str, Enum):
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
```

### Aggregate Types

```python
class AggregateType(str, Enum):
    ASSET = "ASSET"
    CABLE = "CABLE"
    EDGE = "EDGE"
    RULE = "RULE"
    PACKAGE = "PACKAGE"
    BATCH = "BATCH"
```

### Event Payload Structure

```json
{
  "before": {
    "tag": "P-101",
    "type": "PUMP",
    "properties": {"hp": null}
  },
  "after": {
    "tag": "P-101",
    "type": "PUMP",
    "properties": {"hp": 50}
  },
  "diff": [
    {"field": "properties.hp", "old": null, "new": 50}
  ],
  "context": {
    "rule_name": "Set Motor HP",
    "triggered_by": "user_action"
  }
}
```

### Correlation Pattern

Events from the same execution batch share a `correlation_id`:

```
Batch corr-abc123:
├── BATCH_STARTED (seq: 0)
├── RULE_EXECUTION_STARTED "Create Motor" (seq: 1)
├── ASSET_CREATED P-101-M (seq: 2, causation: seq 1)
├── ASSET_CREATED P-102-M (seq: 3, causation: seq 1)
├── RULE_EXECUTION_STARTED "Size Cable" (seq: 4)
├── CABLE_CREATED P-101-M-CBL (seq: 5, causation: seq 4)
├── CABLE_CREATED P-102-M-CBL (seq: 6, causation: seq 4)
└── BATCH_COMPLETED (seq: 7)
```

---

## API Design

### Execute Rules

```http
POST /api/v1/rules/execute
Content-Type: application/json

{
  "project_id": "proj-xxx",
  "mode": "execute",  // or "dry_run"
  "filters": {
    "rule_ids": ["rule-1", "rule-2"],
    "disciplines": ["ELECTRICAL"],
    "action_types": ["CREATE_CHILD", "CREATE_CABLE"],
    "asset_ids": ["asset-1"],
    "asset_types": ["PUMP", "MOTOR"]
  }
}

Response:
{
  "execution_id": "exec-xxx",
  "correlation_id": "corr-xxx",
  "ws_url": "/ws/execution/exec-xxx",
  "status": "started"
}
```

### WebSocket Messages

```typescript
// Connection
ws://host/ws/execution/{execution_id}

// Messages from server
{ "type": "STARTED", "total_rules": 15, "total_assets": 100 }
{ "type": "RULE_START", "rule_id": "xxx", "rule_name": "Create Motor", "progress": 10 }
{ "type": "ACTION", "asset_id": "P-101", "action": "CREATED", "result": "P-101-M" }
{ "type": "PROGRESS", "progress": 65, "actions_completed": 25 }
{ "type": "COMPLETED", "correlation_id": "corr-xxx", "summary": {...} }
{ "type": "ERROR", "message": "...", "asset_id": "..." }
```

### Query Timeline

```http
GET /api/v1/events/timeline
  ?project_id=xxx
  &asset_id=xxx
  &rule_id=xxx
  &discipline=ELECTRICAL
  &event_types=ASSET_CREATED,CABLE_CREATED
  &from=2025-11-01
  &to=2025-11-30
  &page=1
  &limit=50

Response:
{
  "events": [
    {
      "id": "evt-xxx",
      "event_type": "ASSET_CREATED",
      "aggregate_type": "ASSET",
      "aggregate_id": "asset-xxx",
      "payload": {...},
      "rule_id": "rule-xxx",
      "rule_name": "Create Motor",
      "discipline": "ELECTRICAL",
      "timestamp": "2025-11-28T14:32:00Z",
      "correlation_id": "corr-xxx"
    }
  ],
  "total": 150,
  "page": 1,
  "pages": 3
}
```

### Asset History

```http
GET /api/v1/assets/{id}/history

Response:
{
  "asset_id": "asset-xxx",
  "asset_tag": "P-101",
  "history": [
    {
      "event_id": "evt-1",
      "event_type": "ASSET_CREATED",
      "timestamp": "2025-11-25T10:00:00Z",
      "source": "CSV_IMPORT",
      "changes": null,
      "snapshot": {"tag": "P-101", "type": "PUMP", "properties": {}}
    },
    {
      "event_id": "evt-2",
      "event_type": "ASSET_UPDATED",
      "timestamp": "2025-11-26T14:00:00Z",
      "source": "RULE",
      "rule_name": "Set Motor HP",
      "changes": [
        {"field": "properties.hp", "old": null, "new": 50}
      ]
    },
    {
      "event_id": "evt-3",
      "event_type": "RELATIONSHIP_CREATED",
      "timestamp": "2025-11-28T14:32:00Z",
      "source": "RULE",
      "rule_name": "Create Motor",
      "related_entity": {"type": "ASSET", "id": "xxx", "tag": "P-101-M"}
    }
  ]
}
```

### Rollback

```http
POST /api/v1/rules/rollback
Content-Type: application/json

{
  "correlation_id": "corr-xxx"
}

Response:
{
  "status": "rolled_back",
  "correlation_id": "corr-xxx",
  "rolled_back_events": 25,
  "restored_entities": {
    "assets_deleted": 15,
    "cables_deleted": 8,
    "edges_deleted": 15
  },
  "rollback_event_id": "evt-rollback-xxx"
}
```

---

## Database Schema

### workflow_events

```sql
CREATE TABLE workflow_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Event identification
    event_type VARCHAR(50) NOT NULL,
    aggregate_type VARCHAR(30) NOT NULL,
    aggregate_id VARCHAR(100),

    -- Context
    project_id VARCHAR REFERENCES projects(id) NOT NULL,
    rule_id VARCHAR REFERENCES rule_definitions(id),
    discipline VARCHAR(30),

    -- Payload
    payload JSONB NOT NULL DEFAULT '{}',
    metadata JSONB DEFAULT '{}',

    -- Correlation (for batch operations)
    correlation_id UUID NOT NULL,
    causation_id UUID,
    sequence_num BIGINT NOT NULL DEFAULT 0,

    -- Audit
    user_id VARCHAR REFERENCES users(id),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_rolled_back BOOLEAN NOT NULL DEFAULT FALSE,

    -- Constraints
    CONSTRAINT valid_event_type CHECK (event_type IN (
        'ASSET_CREATED', 'ASSET_UPDATED', 'ASSET_DELETED',
        'CABLE_CREATED', 'CABLE_UPDATED', 'CABLE_DELETED',
        'RELATIONSHIP_CREATED', 'RELATIONSHIP_DELETED',
        'RULE_EXECUTION_STARTED', 'RULE_EXECUTED', 'RULE_SKIPPED', 'RULE_ERROR',
        'RULE_EXECUTION_COMPLETED', 'BATCH_STARTED', 'BATCH_COMPLETED',
        'BATCH_ROLLED_BACK', 'CSV_IMPORTED', 'ROLLBACK'
    ))
);

-- Indexes for common queries
CREATE INDEX ix_workflow_events_project_time ON workflow_events(project_id, timestamp DESC);
CREATE INDEX ix_workflow_events_aggregate ON workflow_events(aggregate_type, aggregate_id);
CREATE INDEX ix_workflow_events_correlation ON workflow_events(correlation_id);
CREATE INDEX ix_workflow_events_rule ON workflow_events(rule_id) WHERE rule_id IS NOT NULL;
CREATE INDEX ix_workflow_events_discipline ON workflow_events(discipline) WHERE discipline IS NOT NULL;
CREATE INDEX ix_workflow_events_type ON workflow_events(event_type);
```

### execution_snapshots

```sql
CREATE TABLE execution_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    correlation_id UUID UNIQUE NOT NULL,
    project_id VARCHAR REFERENCES projects(id) NOT NULL,

    -- Snapshot data
    snapshot_data JSONB NOT NULL,
    events_count INT NOT NULL DEFAULT 0,

    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    executed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    rolled_back_at TIMESTAMPTZ,
    rolled_back_by VARCHAR REFERENCES users(id),

    CONSTRAINT valid_status CHECK (status IN ('ACTIVE', 'ROLLED_BACK'))
);

CREATE INDEX ix_execution_snapshots_project ON execution_snapshots(project_id);
CREATE INDEX ix_execution_snapshots_status ON execution_snapshots(status);
```

---

## Frontend Components

### RuleExecutionPanel

Main panel for executing rules with filters and real-time progress.

**Features:**
- Multi-select filters (discipline, rule type, assets, rules)
- Dry run preview with summary
- Execute button with confirmation
- Real-time progress bar
- Live action log (scrolling)
- Cancel execution button

### WorkflowTimeline

Vertical timeline showing all workflow events with filters.

**Features:**
- Date range picker
- Multi-criteria filters (asset, rule, discipline, event type)
- Grouped by correlation_id (batch)
- Expandable event details
- Rollback button per batch
- Pagination with infinite scroll

### AssetHistoryPanel

Detailed history view for a single asset.

**Features:**
- Vertical timeline of changes
- Side-by-side diff view
- Version selector
- Related entities links
- Export history button

---

## Implementation Phases

### Phase 1: Event Store Foundation (Day 1-2)

**Backend:**
- [ ] Create `WorkflowEvent` SQLAlchemy model
- [ ] Create `ExecutionSnapshot` SQLAlchemy model
- [ ] Generate Alembic migration
- [ ] Create `EventStore` service class
  - `emit(event_type, aggregate_type, aggregate_id, payload, ...)`
  - `query(filters) -> List[WorkflowEvent]`
  - `get_by_correlation(correlation_id) -> List[WorkflowEvent]`
- [ ] Create `SnapshotService` class
  - `create_snapshot(correlation_id, entities)`
  - `restore_snapshot(correlation_id)`

**Tests:**
- [ ] Unit tests for EventStore
- [ ] Unit tests for SnapshotService

### Phase 2: Real-time Pipeline (Day 2-3)

**Backend:**
- [ ] Create WebSocket endpoint `/ws/execution/{id}`
- [ ] Create `ExecutionManager` class (coordinates execution + events)
- [ ] Update `RuleEngine.apply_rules()` to emit events
- [ ] Create `POST /rules/execute` with filters
- [ ] Implement dry_run mode

**Frontend:**
- [ ] Create `useExecutionSocket` hook
- [ ] Create `RuleExecutionPanel` component
- [ ] Create execution progress UI
- [ ] Create filter components

**Tests:**
- [ ] WebSocket integration tests
- [ ] Frontend component tests

### Phase 3: Traceability UI (Day 4-5)

**Backend:**
- [ ] Create `GET /events/timeline` endpoint
- [ ] Create `GET /assets/{id}/history` endpoint
- [ ] Create `POST /rules/rollback` endpoint
- [ ] Implement rollback logic

**Frontend:**
- [ ] Create `WorkflowTimeline` component
- [ ] Create `AssetHistoryPanel` component
- [ ] Create diff view component
- [ ] Add rollback confirmation modal

**Tests:**
- [ ] Timeline API tests
- [ ] History API tests
- [ ] Rollback tests
- [ ] E2E tests

---

## Consequences

### Positive

1. **Complete Audit Trail** - Every change is recorded immutably
2. **Time Travel** - Can reconstruct state at any point in time
3. **Rollback Safety** - Undo mistakes with confidence
4. **Real-time UX** - Users see progress immediately
5. **Debugging** - Easy to trace what happened and why
6. **Compliance** - Meets engineering audit requirements

### Negative

1. **Storage Growth** - Events accumulate (mitigate with archival strategy)
2. **Query Complexity** - Need proper indexes for performance
3. **Migration** - Existing data needs event backfill

### Risks

1. **WebSocket Reliability** - Need reconnection handling
2. **Large Batches** - May need pagination for huge executions
3. **Concurrent Edits** - Need to handle conflicts

---

## References

- [Event Sourcing Pattern](https://martinfowler.com/eaaDev/EventSourcing.html)
- [CQRS Pattern](https://martinfowler.com/bliki/CQRS.html)
- Martin Fowler - Event Sourcing
- Greg Young - CQRS and Event Sourcing

---

**Approved:** 2025-11-28
**Implementation Start:** 2025-12-02 (MVP Week 2)
