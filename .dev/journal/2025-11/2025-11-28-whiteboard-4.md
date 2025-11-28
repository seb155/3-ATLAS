# Whiteboard Session #4: Rule Engine Event Sourcing

**Date:** 2025-11-28
**Session:** Whiteboard #4
**Duration:** ~2 hours
**Branch:** `claude/rule-engine-whiteboard-4-01MTDo3fGp38E1FrgKNQpxem`

---

## Session Overview

Architecture and planning session for implementing Event Sourcing in the SYNAPSE Rule Engine. Focus on complete traceability, real-time execution feedback, and rollback capability.

---

## Decisions Made

### Architecture Choice: Event Sourcing (A + B + D)

After reviewing options, we decided on a combined approach:

| Option | Description | Included |
|--------|-------------|----------|
| **A** | Event Sourcing Foundation | Yes |
| **B** | Real-time WebSocket Pipeline | Yes |
| **C** | Dry Run / Preview Mode | Yes (bonus) |
| **D** | Asset Changelog + Diff View | Yes |

### Event Granularity

Events will be tracked at multiple levels with full filter support:

- **By Asset** - Complete history of any asset
- **By Rule** - All executions of a specific rule
- **By Discipline** - ELECTRICAL, AUTOMATION, MECHANICAL, etc.
- **By Batch** - All events from a single execution (correlation_id)
- **Mixed Filters** - Combine any of the above

### Rollback Scope

- Rollback operates at **batch level** (correlation_id)
- Uses pre-execution **snapshots** for safe restoration
- Creates new ROLLBACK events for audit trail
- Marks original events as `is_rolled_back = true`

---

## Documentation Created

| Document | Path | Purpose |
|----------|------|---------|
| **ADR-003** | `.dev/decisions/003-rule-engine-event-sourcing.md` | Architecture decision record |
| **Tech Spec** | `docs/developer-guide/rule-engine-event-sourcing.md` | Full technical specification |
| **API Reference** | `docs/reference/rule-engine-api.md` | Complete API documentation |
| **Implementation Checklist** | `.dev/roadmap/backlog/rule-engine-event-sourcing.md` | Task checklist with phases |
| **Week 2 Sprint** | `.dev/roadmap/mvp-week-2-sprint.md` | Day-by-day sprint plan |

---

## Key Technical Decisions

### 1. Database Schema

Two new tables:
- `workflow_events` - Immutable event store (append-only)
- `execution_snapshots` - Pre-execution state for rollback

### 2. Event Types (15)

```
ASSET_CREATED, ASSET_UPDATED, ASSET_DELETED
CABLE_CREATED, CABLE_UPDATED, CABLE_DELETED
RELATIONSHIP_CREATED, RELATIONSHIP_DELETED
RULE_EXECUTION_STARTED, RULE_EXECUTED, RULE_SKIPPED, RULE_ERROR, RULE_EXECUTION_COMPLETED
BATCH_STARTED, BATCH_COMPLETED, BATCH_ROLLED_BACK
CSV_IMPORTED, ROLLBACK
```

### 3. Correlation Pattern

All events in a batch share `correlation_id`:
- Enables batch rollback
- Groups related events in timeline
- Links cause → effect via `causation_id`

### 4. WebSocket Protocol

Real-time updates during execution:
```
STARTED → RULE_START → ACTION (per asset) → PROGRESS → RULE_COMPLETE → COMPLETED
```

### 5. API Design

| Endpoint | Purpose |
|----------|---------|
| `POST /rules/execute` | Execute rules with filters |
| `POST /rules/rollback` | Rollback batch by correlation_id |
| `GET /events/timeline` | Query events with filters |
| `GET /events/assets/{id}/history` | Asset-specific history |

---

## Implementation Plan (Week 2: Dec 2-6)

| Day | Focus | Key Deliverables |
|-----|-------|------------------|
| **1** | Models + Migration | `WorkflowEvent`, `ExecutionSnapshot` models |
| **2** | Services | `EventStore`, `SnapshotService`, `RollbackService` |
| **3** | Execute Pipeline | API endpoint, WebSocket, `RuleExecutionPanel` |
| **4** | Traceability UI | `WorkflowTimeline`, `AssetHistoryPanel`, filters |
| **5** | Polish + Testing | Integration tests, E2E, documentation |

---

## Frontend Components Planned

```
src/components/
├── rules/
│   ├── RuleExecutionPanel.tsx      # Execute with filters + progress
│   ├── WorkflowTimeline.tsx        # Event timeline with filters
│   ├── AssetHistoryPanel.tsx       # Single asset history
│   └── RollbackConfirmModal.tsx    # Rollback confirmation
├── common/
│   └── DiffViewer.tsx              # JSON diff display
└── hooks/
    └── useExecutionSocket.ts       # WebSocket hook
```

---

## Questions Resolved

| Question | Decision |
|----------|----------|
| Event granularity? | Multi-level: asset, rule, discipline, batch + mixed |
| Rollback scope? | Batch level (correlation_id) |
| Dry run needed? | Yes, implement as bonus |
| WebSocket or polling? | WebSocket for real-time |
| Storage strategy? | Plan archival post-MVP |

---

## Next Steps

1. **Immediate:** Review this documentation
2. **Dec 2 (Day 1):** Start implementation with models + migration
3. **During Week:** Follow day-by-day sprint plan
4. **Dec 6 (Day 5):** Demo rehearsal

---

## Files Changed This Session

### Created
- `.dev/decisions/003-rule-engine-event-sourcing.md`
- `docs/developer-guide/rule-engine-event-sourcing.md`
- `docs/reference/rule-engine-api.md`
- `.dev/roadmap/backlog/rule-engine-event-sourcing.md`
- `.dev/roadmap/mvp-week-2-sprint.md`
- `.dev/journal/2025-11/2025-11-28-whiteboard-4.md` (this file)

### No Code Changes
This was a planning/architecture session. Implementation starts Dec 2.

---

## Session Summary

Completed comprehensive planning for Rule Engine Event Sourcing:

- Architecture decision documented (ADR-003)
- Full technical specification written
- API reference with all endpoints
- Day-by-day sprint plan for Week 2
- Implementation checklist with ~100 tasks

**Ready for implementation starting Dec 2, 2025.**

---

**Tags:** #whiteboard #architecture #rule-engine #event-sourcing #mvp-week-2
