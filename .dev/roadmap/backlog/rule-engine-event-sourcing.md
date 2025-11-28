# Rule Engine Event Sourcing - Implementation Checklist

**Status:** PLANNED
**Sprint:** MVP Week 2 (Dec 2-6, 2025)
**ADR:** [003-rule-engine-event-sourcing](../../decisions/003-rule-engine-event-sourcing.md)
**Tech Spec:** [rule-engine-event-sourcing.md](../../../docs/developer-guide/rule-engine-event-sourcing.md)
**API Reference:** [rule-engine-api.md](../../../docs/reference/rule-engine-api.md)

---

## Overview

Implement Event Sourcing architecture for the Rule Engine to provide:
- Complete audit trail (traceability)
- Real-time execution feedback (WebSocket)
- Rollback capability
- Multi-criteria filtering (by asset, rule, discipline)

---

## Phase 1: Event Store Foundation (Day 1-2)

### Database Models

- [ ] Create `app/models/workflow_events.py`
  - [ ] `WorkflowEventType` enum (15 event types)
  - [ ] `AggregateType` enum (6 aggregate types)
  - [ ] `WorkflowEvent` model with all fields
  - [ ] `SnapshotStatus` enum
  - [ ] `ExecutionSnapshot` model
  - [ ] Indexes for performance

- [ ] Create Alembic migration
  - [ ] `workflow_events` table
  - [ ] `execution_snapshots` table
  - [ ] All indexes
  - [ ] Run migration: `alembic upgrade head`
  - [ ] Verify tables in database

### Backend Services

- [ ] Create `app/services/event_store.py`
  - [ ] `EventStore` class
    - [ ] `start_batch()` - Initialize correlation_id
    - [ ] `emit()` - Create event
    - [ ] `query()` - Query with filters
    - [ ] `get_by_correlation()` - Get batch events
    - [ ] `get_asset_history()` - Get asset events
  - [ ] `SnapshotService` class
    - [ ] `create_snapshot()` - Store pre-execution state
    - [ ] `get_by_correlation()` - Retrieve snapshot
    - [ ] `mark_rolled_back()` - Update status
    - [ ] `list_active()` - List active snapshots

- [ ] Create `app/services/rollback_service.py`
  - [ ] `RollbackService` class
    - [ ] `rollback()` - Full rollback implementation
    - [ ] Handle ASSET_CREATED events
    - [ ] Handle CABLE_CREATED events
    - [ ] Handle RELATIONSHIP_CREATED events
    - [ ] Handle ASSET_UPDATED events
    - [ ] Mark events as rolled back
    - [ ] Update snapshot status

### Unit Tests

- [ ] Create `tests/test_event_store.py`
  - [ ] Test `emit()` creates event
  - [ ] Test batch correlation
  - [ ] Test query filters
  - [ ] Test asset history

- [ ] Create `tests/test_snapshot_service.py`
  - [ ] Test create snapshot
  - [ ] Test retrieve snapshot
  - [ ] Test mark rolled back

- [ ] Create `tests/test_rollback_service.py`
  - [ ] Test rollback deletes created assets
  - [ ] Test rollback deletes created cables
  - [ ] Test rollback restores updated assets
  - [ ] Test rollback marks events

**Phase 1 Deliverables:**
- [ ] All models created and migrated
- [ ] EventStore service functional
- [ ] SnapshotService functional
- [ ] RollbackService functional
- [ ] Unit tests passing (>70% coverage)

---

## Phase 2: Real-time Pipeline (Day 2-3)

### WebSocket Infrastructure

- [ ] Create `app/api/websocket/execution.py`
  - [ ] `ExecutionWebSocket` class
    - [ ] `connect()` - Accept connection
    - [ ] `disconnect()` - Remove connection
    - [ ] `send_message()` - Send to specific client
    - [ ] `broadcast_progress()` - Send progress update
  - [ ] `WSMessageType` constants
  - [ ] WebSocket route handler

- [ ] Register WebSocket in `app/main.py`
  - [ ] Add WebSocket route `/ws/execution/{id}`

### API Endpoints

- [ ] Create `app/api/endpoints/rule_execution.py`
  - [ ] `ExecuteRulesRequest` schema
  - [ ] `ExecutionFilters` schema
  - [ ] `ExecuteRulesResponse` schema
  - [ ] `POST /rules/execute` endpoint
    - [ ] Validate filters
    - [ ] Start batch (correlation_id)
    - [ ] Return WebSocket URL
  - [ ] `POST /rules/rollback` endpoint
    - [ ] Validate correlation_id
    - [ ] Call RollbackService
    - [ ] Return summary

- [ ] Update `RuleEngine.apply_rules()`
  - [ ] Accept WebSocket callback
  - [ ] Emit BATCH_STARTED event
  - [ ] Emit RULE_EXECUTION_STARTED per rule
  - [ ] Emit ASSET_CREATED/UPDATED per action
  - [ ] Emit RULE_EXECUTION_COMPLETED per rule
  - [ ] Emit BATCH_COMPLETED event
  - [ ] Create snapshot before execution
  - [ ] Send WebSocket messages

- [ ] Implement dry_run mode
  - [ ] Preview changes without persisting
  - [ ] Return preview summary

### Frontend Hook

- [ ] Create `src/hooks/useExecutionSocket.ts`
  - [ ] WebSocket connection management
  - [ ] Message handling (all types)
  - [ ] Progress state tracking
  - [ ] Actions accumulation
  - [ ] Summary extraction
  - [ ] Error handling
  - [ ] Reconnection logic

- [ ] Create `src/services/ruleExecutionApi.ts`
  - [ ] `executeRules()` - POST /rules/execute
  - [ ] `rollbackExecution()` - POST /rules/rollback

### Frontend Components

- [ ] Create `src/components/rules/RuleExecutionPanel.tsx`
  - [ ] Filter section
    - [ ] Discipline multi-select
    - [ ] Action type multi-select
    - [ ] Asset type multi-select
    - [ ] Rule multi-select
  - [ ] Preview section (dry run results)
  - [ ] Execute button with confirmation
  - [ ] Progress bar
  - [ ] Live action log (scrolling)
  - [ ] Summary on completion
  - [ ] Cancel button

### Integration Tests

- [ ] Create `tests/test_rule_execution_api.py`
  - [ ] Test execute with filters
  - [ ] Test dry run mode
  - [ ] Test rollback endpoint

- [ ] Create WebSocket integration test
  - [ ] Test message flow
  - [ ] Test progress updates

**Phase 2 Deliverables:**
- [ ] WebSocket endpoint functional
- [ ] Execute endpoint with filters
- [ ] Dry run mode working
- [ ] useExecutionSocket hook complete
- [ ] RuleExecutionPanel component
- [ ] Integration tests passing

---

## Phase 3: Traceability UI (Day 4-5)

### API Endpoints

- [ ] Create `app/api/endpoints/events.py`
  - [ ] `GET /events/timeline` endpoint
    - [ ] All filter parameters
    - [ ] Pagination
    - [ ] Date range
  - [ ] `GET /events/assets/{id}/history` endpoint
    - [ ] Full asset history
    - [ ] Related entities
  - [ ] `GET /events/batch/{correlation_id}` endpoint
    - [ ] Batch events
    - [ ] Summary
    - [ ] Rollback status

- [ ] Register routes in `app/main.py`

### Frontend Components

- [ ] Create `src/components/rules/WorkflowTimeline.tsx`
  - [ ] Filter bar
    - [ ] Date range picker
    - [ ] Asset filter
    - [ ] Rule filter
    - [ ] Discipline filter
    - [ ] Event type filter
  - [ ] Timeline view
    - [ ] Grouped by correlation_id
    - [ ] Expandable event details
    - [ ] Rollback button per batch
  - [ ] Pagination / infinite scroll
  - [ ] Empty state
  - [ ] Loading state

- [ ] Create `src/components/rules/AssetHistoryPanel.tsx`
  - [ ] Asset header
  - [ ] Timeline view
  - [ ] Diff viewer
    - [ ] Side-by-side comparison
    - [ ] Field highlighting
    - [ ] Version selector
  - [ ] Related entities list
  - [ ] Export history button

- [ ] Create `src/components/rules/RollbackConfirmModal.tsx`
  - [ ] Summary of batch to rollback
  - [ ] Warning about destructive action
  - [ ] Confirm/Cancel buttons
  - [ ] Loading state during rollback

- [ ] Create `src/components/common/DiffViewer.tsx`
  - [ ] JSON diff display
  - [ ] Color-coded changes (red/green)
  - [ ] Collapsible sections

### Frontend Integration

- [ ] Update `src/stores/ruleStore.ts` (or create)
  - [ ] Timeline state
  - [ ] Filters state
  - [ ] Selected batch state
  - [ ] Asset history state

- [ ] Add routes in `App.tsx`
  - [ ] `/rules/execution` - RuleExecutionPanel
  - [ ] `/rules/timeline` - WorkflowTimeline
  - [ ] `/assets/:id/history` - AssetHistoryPanel

- [ ] Update Sidebar navigation
  - [ ] Add Rule Execution link
  - [ ] Add Timeline link

### Component Tests

- [ ] Create `WorkflowTimeline.test.tsx`
  - [ ] Test filter changes
  - [ ] Test event display
  - [ ] Test rollback button

- [ ] Create `AssetHistoryPanel.test.tsx`
  - [ ] Test history display
  - [ ] Test diff viewer

- [ ] Create `DiffViewer.test.tsx`
  - [ ] Test diff highlighting

### E2E Tests

- [ ] Create `e2e/rule-execution.spec.ts`
  - [ ] Test full execution flow
  - [ ] Test timeline viewing
  - [ ] Test rollback flow

**Phase 3 Deliverables:**
- [ ] Timeline endpoint functional
- [ ] Asset history endpoint functional
- [ ] WorkflowTimeline component
- [ ] AssetHistoryPanel component
- [ ] DiffViewer component
- [ ] Full integration working
- [ ] E2E tests passing

---

## Quality Checklist

### Backend

- [ ] All endpoints have OpenAPI documentation
- [ ] All services have type hints
- [ ] Error handling for all edge cases
- [ ] Logging for debugging
- [ ] Performance: timeline query < 200ms
- [ ] Test coverage > 70%

### Frontend

- [ ] All components have TypeScript types
- [ ] Loading states for async operations
- [ ] Error boundaries
- [ ] Responsive design
- [ ] Keyboard navigation
- [ ] Test coverage > 70%

### Documentation

- [ ] ADR-003 complete
- [ ] Tech spec complete
- [ ] API reference complete
- [ ] User guide section (how to use)

---

## File Inventory

### New Files (Backend)

```
apps/synapse/backend/
├── app/
│   ├── models/
│   │   └── workflow_events.py           # NEW
│   ├── services/
│   │   ├── event_store.py               # NEW
│   │   └── rollback_service.py          # NEW
│   └── api/
│       ├── endpoints/
│       │   ├── rule_execution.py        # NEW
│       │   └── events.py                # NEW
│       └── websocket/
│           └── execution.py             # NEW
├── alembic/versions/
│   └── xxx_add_workflow_events.py       # NEW
└── tests/
    ├── test_event_store.py              # NEW
    ├── test_rollback_service.py         # NEW
    ├── test_rule_execution_api.py       # NEW
    └── test_events_api.py               # NEW
```

### New Files (Frontend)

```
apps/synapse/frontend/src/
├── hooks/
│   └── useExecutionSocket.ts            # NEW
├── components/
│   ├── rules/
│   │   ├── RuleExecutionPanel.tsx       # NEW
│   │   ├── WorkflowTimeline.tsx         # NEW
│   │   ├── AssetHistoryPanel.tsx        # NEW
│   │   └── RollbackConfirmModal.tsx     # NEW
│   └── common/
│       └── DiffViewer.tsx               # NEW
├── services/
│   └── ruleExecutionApi.ts              # NEW
└── stores/
    └── ruleStore.ts                     # NEW or MODIFY
```

### Modified Files

```
apps/synapse/backend/app/
├── main.py                              # Add routes + websocket
├── services/
│   └── rule_engine.py                   # Add event emission

apps/synapse/frontend/src/
├── App.tsx                              # Add routes
└── components/layout/
    └── Sidebar.tsx                      # Add navigation items
```

---

## Dependencies

### Backend

```
# No new dependencies required
# Uses existing: SQLAlchemy, FastAPI, WebSockets
```

### Frontend

```
# No new dependencies required
# Uses existing: React, Zustand, Tailwind, Shadcn/ui
```

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| WebSocket reliability | Implement reconnection with exponential backoff |
| Large batch performance | Pagination + batch WebSocket messages |
| Rollback data integrity | Transaction wrapping + snapshot validation |
| Storage growth | Plan for event archival strategy (post-MVP) |

---

## Success Criteria

- [ ] Execute rules with filters works end-to-end
- [ ] Real-time progress visible in UI
- [ ] Timeline shows all events with filters
- [ ] Asset history shows complete diff
- [ ] Rollback restores previous state correctly
- [ ] Test coverage > 70%
- [ ] No performance regressions
- [ ] Demo-ready for Dec 20

---

**Created:** 2025-11-28 (Whiteboard Session #4)
**Last Updated:** 2025-11-28
