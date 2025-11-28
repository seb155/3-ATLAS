# MVP Week 2 Sprint: Rule Engine + Workflow Logs

**Status:** PLANNED
**Dates:** Dec 2-6, 2025
**Priority:** CRITICAL (MVP)

---

## Goal

Implement Event Sourcing for the Rule Engine with real-time execution, complete traceability, and rollback capability.

**Demo Target:** Show engineers executing rules with live feedback, viewing execution history, and rolling back changes.

---

## Sprint Overview

| Day | Focus | Deliverables |
|-----|-------|--------------|
| **Day 1** | Event Store Foundation | Models, migration, EventStore service |
| **Day 2** | Event Store + WebSocket | SnapshotService, RollbackService, WebSocket endpoint |
| **Day 3** | Execution Pipeline | Execute API, dry run, RuleExecutionPanel |
| **Day 4** | Traceability UI | Timeline API, WorkflowTimeline, AssetHistoryPanel |
| **Day 5** | Polish + Testing | Integration tests, E2E, bug fixes, documentation |

---

## Day 1: Event Store Foundation

### Morning (3h)

- [ ] Create `app/models/workflow_events.py`
  - [ ] `WorkflowEventType` enum (15 types)
  - [ ] `AggregateType` enum (6 types)
  - [ ] `WorkflowEvent` model
  - [ ] `ExecutionSnapshot` model

- [ ] Create Alembic migration
  - [ ] Run: `alembic revision --autogenerate -m "add_workflow_events"`
  - [ ] Apply: `alembic upgrade head`
  - [ ] Verify tables

### Afternoon (4h)

- [ ] Create `app/services/event_store.py`
  - [ ] `EventStore.start_batch()`
  - [ ] `EventStore.emit()`
  - [ ] `EventStore.query()` with all filters
  - [ ] `EventStore.get_by_correlation()`
  - [ ] `EventStore.get_asset_history()`

- [ ] Write unit tests for EventStore
  - [ ] Test emit creates event
  - [ ] Test batch correlation
  - [ ] Test query filters
  - [ ] Run: `pytest tests/test_event_store.py`

**Day 1 Exit Criteria:**
- [ ] `workflow_events` table exists
- [ ] `execution_snapshots` table exists
- [ ] EventStore can emit and query events
- [ ] Unit tests passing

---

## Day 2: Services + WebSocket

### Morning (3h)

- [ ] Create `app/services/snapshot_service.py` (or in event_store.py)
  - [ ] `SnapshotService.create_snapshot()`
  - [ ] `SnapshotService.get_by_correlation()`
  - [ ] `SnapshotService.mark_rolled_back()`

- [ ] Create `app/services/rollback_service.py`
  - [ ] `RollbackService.rollback()`
  - [ ] Handle asset rollback
  - [ ] Handle cable rollback
  - [ ] Handle edge rollback
  - [ ] Handle property restore

- [ ] Write unit tests for Rollback
  - [ ] Test rollback deletes created entities
  - [ ] Test rollback restores properties
  - [ ] Run: `pytest tests/test_rollback_service.py`

### Afternoon (4h)

- [ ] Create `app/api/websocket/execution.py`
  - [ ] `ExecutionWebSocket` class
  - [ ] Message types (STARTED, PROGRESS, ACTION, COMPLETED, ERROR)
  - [ ] WebSocket handler function

- [ ] Register WebSocket in `app/main.py`
  - [ ] Add route `/ws/execution/{execution_id}`
  - [ ] Test with wscat: `wscat -c ws://localhost:8001/ws/execution/test`

**Day 2 Exit Criteria:**
- [ ] SnapshotService functional
- [ ] RollbackService functional
- [ ] WebSocket endpoint accepting connections
- [ ] Unit tests passing

---

## Day 3: Execution Pipeline

### Morning (3h)

- [ ] Create `app/api/endpoints/rule_execution.py`
  - [ ] `POST /rules/execute` endpoint
    - [ ] Accept filters (disciplines, rule_ids, asset_ids, etc.)
    - [ ] Start batch, create snapshot
    - [ ] Return execution_id + ws_url
  - [ ] `POST /rules/rollback` endpoint

- [ ] Update `RuleEngine.apply_rules()`
  - [ ] Accept optional filters
  - [ ] Emit events during execution
  - [ ] Send WebSocket messages
  - [ ] Create snapshot before execution

- [ ] Implement dry_run mode
  - [ ] Preview without persisting
  - [ ] Return summary

### Afternoon (4h)

- [ ] Create `src/hooks/useExecutionSocket.ts`
  - [ ] WebSocket connection
  - [ ] Message handling
  - [ ] Progress state
  - [ ] Actions list

- [ ] Create `src/components/rules/RuleExecutionPanel.tsx`
  - [ ] Filter section (multi-selects)
  - [ ] Preview/Dry run section
  - [ ] Execute button
  - [ ] Progress bar
  - [ ] Live action log
  - [ ] Summary on completion

- [ ] Test execution flow
  - [ ] Start execution from UI
  - [ ] Verify WebSocket messages
  - [ ] Verify events in database

**Day 3 Exit Criteria:**
- [ ] Execute endpoint working
- [ ] Filters working (discipline, rule, asset)
- [ ] WebSocket sending progress
- [ ] RuleExecutionPanel functional
- [ ] Dry run working

---

## Day 4: Traceability UI

### Morning (3h)

- [ ] Create `app/api/endpoints/events.py`
  - [ ] `GET /events/timeline` endpoint
    - [ ] All filters (asset, rule, discipline, date, type)
    - [ ] Pagination
  - [ ] `GET /events/assets/{id}/history` endpoint
    - [ ] Full asset history
    - [ ] Related entities
  - [ ] `GET /events/batch/{correlation_id}` endpoint

- [ ] Register routes in `app/main.py`

- [ ] Test APIs with curl/Postman

### Afternoon (4h)

- [ ] Create `src/components/rules/WorkflowTimeline.tsx`
  - [ ] Filter bar (date, asset, rule, discipline)
  - [ ] Timeline view (grouped by batch)
  - [ ] Expandable event details
  - [ ] Rollback button per batch
  - [ ] Pagination

- [ ] Create `src/components/rules/AssetHistoryPanel.tsx`
  - [ ] Asset header info
  - [ ] Timeline of changes
  - [ ] Diff viewer (before/after)
  - [ ] Related entities

- [ ] Create `src/components/common/DiffViewer.tsx`
  - [ ] JSON diff display
  - [ ] Color coding (red=removed, green=added)

- [ ] Add routes in App.tsx
  - [ ] `/rules/execution`
  - [ ] `/rules/timeline`
  - [ ] `/assets/:id/history`

**Day 4 Exit Criteria:**
- [ ] Timeline API working with filters
- [ ] Asset history API working
- [ ] WorkflowTimeline component
- [ ] AssetHistoryPanel component
- [ ] Navigation working

---

## Day 5: Polish + Testing

### Morning (3h)

- [ ] Integration tests
  - [ ] `test_rule_execution_api.py`
  - [ ] `test_events_api.py`
  - [ ] Test rollback end-to-end

- [ ] Frontend tests
  - [ ] `RuleExecutionPanel.test.tsx`
  - [ ] `WorkflowTimeline.test.tsx`
  - [ ] `useExecutionSocket.test.ts`

- [ ] Fix any bugs found

### Afternoon (4h)

- [ ] E2E test
  - [ ] Full execution flow
  - [ ] Timeline viewing
  - [ ] Rollback flow

- [ ] UI polish
  - [ ] Loading states
  - [ ] Error states
  - [ ] Empty states
  - [ ] Toast notifications

- [ ] Documentation
  - [ ] Update CHANGELOG.md
  - [ ] Update README.md
  - [ ] Create demo script

- [ ] Manual testing checklist:
  - [ ] Execute rules with discipline filter
  - [ ] Execute rules with asset filter
  - [ ] View real-time progress
  - [ ] View timeline
  - [ ] Filter timeline by asset
  - [ ] Filter timeline by rule
  - [ ] View asset history
  - [ ] Perform rollback
  - [ ] Verify rollback worked

**Day 5 Exit Criteria:**
- [ ] All tests passing (>70% coverage)
- [ ] No critical bugs
- [ ] Documentation updated
- [ ] Demo ready

---

## Technical References

- **ADR:** `.dev/decisions/003-rule-engine-event-sourcing.md`
- **Tech Spec:** `docs/developer-guide/rule-engine-event-sourcing.md`
- **API Reference:** `docs/reference/rule-engine-api.md`
- **Implementation Checklist:** `.dev/roadmap/backlog/rule-engine-event-sourcing.md`

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Backend test coverage | >70% |
| Frontend test coverage | >70% |
| Timeline query latency | <200ms |
| WebSocket message latency | <100ms |
| Execution with 100 assets | <5 seconds |

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| WebSocket stability | High | Implement reconnection with backoff |
| Large batch performance | Medium | Add pagination, batch messages |
| Rollback data integrity | High | Use transactions, verify in tests |
| Storage growth | Low | Plan archival (post-MVP) |

---

## Definition of Done

- [ ] All Day exit criteria met
- [ ] Test coverage >70%
- [ ] No P0/P1 bugs
- [ ] Code reviewed
- [ ] Documentation complete
- [ ] Demo rehearsed

---

**Created:** 2025-11-28 (Whiteboard Session #4)
**Sprint Start:** 2025-12-02
