# ADR-002: DevConsole V3 - Workflow-Centric Architecture

**Status**: Approved  
**Date**: 2025-11-24  
**Deciders**: SYNAPSE Core Team

---

## Context

The current DevConsole (V2) displays logs as a flat list with basic filtering. While functional, it has limitations:
- Difficult to track multi-step operations (imports, rule executions)
- 200+ individual logs for a single import → overwhelming
- No visual workflow representation
- Limited navigation to entities
- No user/developer mode distinction

We need a **professional-grade** developer console that shows logs as **workflows** with clear hierarchy and status.

---

## Decision

We will rebuild the DevConsole with a **3-level workflow architecture**:

```
WORKFLOW (User action, e.g., "Import Gold Mine")
  └─ JOB (Phase of work, e.g., "Fetch External Assets")
      └─ STEP (Individual log, e.g., "Created P-101")
```

### Key Components

1. **Backend**: Simple WorkflowEngine (no external job scheduler)
2. **Frontend**: Timeline (left) + Details (right) panels
3. **Payload Viewer**: SmartPayloadViewer with entity detection
4. **Modes**: User (simplified) vs Dev (full details)

---

## Alternatives Considered

### Alternative 1: External Job Scheduler (Celery)
**Pros**:
- Battle-tested
- Advanced retry logic
- Distributed workers

**Cons**:
- Added complexity (new service)
- Overkill for current scale
- Learning curve

**Decision**: Rejected. Use FastAPI BackgroundTasks for now, migrate to Celery when scaling.

---

### Alternative 2: Keep Flat Log List
**Pros**:
- Simple implementation
- No backend changes

**Cons**:
- Poor UX for multi-step operations
- Doesn't scale (1000+ logs)
- No workflow visualization

**Decision**: Rejected. Workflow hierarchy provides much better UX.

---

### Alternative 3: Temporal.io Workflow Engine
**Pros**:
- Visual workflow editor
- State management
- Production-grade

**Cons**:
- Heavy (new infrastructure)
- Complex setup
- Not needed at current scale

**Decision**: Rejected. Too complex for current needs.

---

## Consequences

### Positive
✅ **Better UX**: Users see "Import Gold Mine" instead of 50 log lines  
✅ **Navigation**: Click entity tags to navigate  
✅ **Status Tracking**: Visual progress bars for workflows  
✅ **Modes**: User mode hides technical details  
✅ **Scalable**: Can migrate to Celery later without frontend changes  

### Negative
⚠️ **Backend Changes**: Need to update all endpoints to use ActionLogger  
⚠️ **Migration**: Existing logs won't be grouped (only new ones)  
⚠️ **Learning Curve**: Developers must understand workflow concept  

### Neutral
🔄 **Logging Overhead**: Minimal (< 5ms per log)  
🔄 **Storage**: No change (same logs, different structure)  

---

## Implementation Strategy

### Phase 1: Backend Foundation (Week 1)
- Create `WorkflowEngine` and `ActionLogger`
- Enhance `LoggingMiddleware` with user context
- Update 2-3 endpoints as proof-of-concept (Import, Rules)

### Phase 2: Frontend Core (Week 1-2)
- Build DevConsoleV3 components
- Implement Timeline/Details panels
- Add SmartPayloadViewer

### Phase 3: Integration (Week 2)
- Replace old DevConsole
- Update all endpoints
- User testing

### Phase 4: Polish (Week 3)
- Performance optimization
- Documentation
- Training materials

---

## Technical Decisions

### Why FastAPI BackgroundTasks (not Celery)?
- ✅ Sufficient for tasks < 5 minutes
- ✅ No new infrastructure
- ✅ Easy to migrate later
- ✅ Works with existing stack

**Threshold for Celery**: When imports exceed 5 minutes OR need distributed workers.

---

### Why @uiw/react-json-view (not react-json-view)?
- ✅ More modern, better maintained
- ✅ Lighter (50% smaller bundle)
- ✅ Better TypeScript support
- ✅ Native dark theme

---

### Why 3 Levels (not 2)?
2 levels (Workflow → Steps) would group logs but lose phase granularity:
```
Import Gold Mine
  ├─ Created P-101    ❌ Hard to see which phase
  ├─ Created P-102
  ├─ Validating...
  └─ Saved to DB
```

3 levels (Workflow → Jobs → Steps) provides clear phases:
```
Import Gold Mine
  ├─ Fetch External   ✅ Clear phases
  │   ├─ Created P-101
  │   └─ Created P-102
  ├─ Validate
  │   └─ Schemas OK
  └─ Save to DB
      └─ 15 items saved
```

---

### Why Stop on Failure (not Best Effort)?
**User Mode** requires predictable behavior:
- ✅ Stop → User knows exactly what happened
- ✅ Notification → Clear error message
- ✅ Resume → Can retry failed job

**Best Effort** would hide partial failures and confuse users.

---

## Monitoring

### Success Metrics
- **Adoption**: % of users who open DevConsole
- **Usage**: Average time spent in DevConsole
- **Errors**: Reduction in support tickets about "what happened?"
- **Performance**: < 16ms render time for 1000 logs

### Rollback Plan
If V3 causes issues:
1. Feature flag to revert to V2
2. Fix V3 issues
3. Gradual rollout (10% → 50% → 100%)

---

## Documentation

- Technical Reference: `docs/reference/devconsole-v3.md`
- Developer Guide: `docs/developer-guide/workflow-engine.md` (to create)
- User Guide: `docs/workflows/using-devconsole.md` (to create)

---

## References

- [Logging Infrastructure](../docs/reference/logging-infrastructure.md)
- [GitHub: react-json-view](https://github.com/mac-s-g/react-json-view)
- [GitHub: @uiw/react-json-view](https://github.com/uiwjs/react-json-view)
- [FastAPI Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)

---

**Approved By**: SYNAPSE Core Team  
**Implementation Start**: 2025-11-24
