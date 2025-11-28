# DevConsole V3 - Technical Reference

**Version**: 3.0.0  
**Status**: In Development  
**Target Release**: v0.2.2

---

## Overview

DevConsole V3 is a professional-grade developer console for SYNAPSE with a **workflow-centric** architecture. It displays logs as hierarchical workflows with jobs and steps, providing both user-friendly and developer-focused views.

---

## Architecture

### Concept: 3-Level Hierarchy

```
WORKFLOW (User action)
  └─ JOB (Phase of work)
      └─ STEP (Individual log)
```

**Example**:
```
Workflow: Import Gold Mine
  ├─ Job 1: Fetch External Assets    [✓ Completed - 2.3s]
  │   ├─ Step: Created P-101
  │   ├─ Step: Created P-102
  │   └─ Step: Created M-101
  ├─ Job 2: Process Data              [▶ Running - 1.8s]
  │   └─ Step: Validating schemas...
  ├─ Job 3: Update Database           [⏸ Pending]
  └─ Job 4: Generate Cables           [⏸ Pending]
```

---

## Components

### Backend

#### WorkflowEngine (`app/services/workflow_engine.py`)
Orchestrates workflow execution without external job scheduler.

**Key Methods**:
- `start_workflow(type, params)` - Create workflow
- `execute_workflow(workflow_id)` - Run jobs sequentially
- `start_job(job_id)` - Begin job execution
- `complete_job(job_id, stats)` - Mark job complete
- `fail_job(job_id, error)` - Mark job as failed (stops workflow)

**Features**:
- Uses FastAPI `BackgroundTasks` for async execution
- Sequential job execution (Job 2 starts after Job 1 completes)
- Auto-stop on failure
- WebSocket notifications for real-time updates

---

#### ActionLogger (`app/services/action_logger.py`)
Groups related logs into hierarchical actions.

**Key Methods**:
- `start_action(type, summary)` → Returns `action_id`
- `log_step(action_id, message, entity_tag, entity_route)`
- `complete_action(action_id, stats)`
- `fail_action(action_id, error, stack)`
- `update_progress(action_id, progress)`

**Enhanced Log Structure**:
```typescript
interface EnhancedLogEntry {
  // Action Grouping
  actionId?: string;           // Groups related logs
  actionType?: string;         // "IMPORT", "RULE_EXECUTION"
  actionSummary?: string;      // "Import Gold Mine"
  actionStatus?: "RUNNING" | "COMPLETED" | "FAILED";
  actionStats?: {
    duration?: number;         // milliseconds
    itemsProcessed?: number;
    itemsCreated?: number;
  };
  
  // User Context
  userId?: string;
  userName?: string;
  
  // Navigation
  entityTag?: string;          // "P-101"
  entityRoute?: string;        // "/assets/123"
  
  // Performance
  responseTime?: number;       // API latency
}
```

---

#### LoggingMiddleware (`app/middleware/logging_middleware.py`)
Captures all HTTP requests with enhanced context.

**Enhancements**:
- Extract user from JWT token
- Calculate response time
- Auto-detect topic from URL path
- Include all context in logs

---

### Frontend

#### Component Structure
```
DevConsoleV3/
├── DevConsoleV3.tsx              # Main container
├── components/
│   ├── Header/
│   │   ├── HeaderBar.tsx         # Mode toggle, filters, status
│   │   ├── FilterBar.tsx         # Multi-filter system
│   │   └── QuickPresets.tsx      # Preset filter combos
│   ├── Timeline/
│   │   ├── TimelinePanel.tsx     # Left panel (workflow list)
│   │   ├── TimelineGroup.tsx     # Workflow item (expandable)
│   │   └── TimelineItem.tsx      # Job/Step item
│   ├── Details/
│   │   ├── DetailsPanel.tsx      # Right panel (selected details)
│   │   ├── OverviewTab.tsx       # Summary view
│   │   ├── SmartPayloadViewer.tsx # JSON with entity detection
│   │   ├── TimelineTab.tsx       # Mini workflow timeline
│   │   └── ActionButtons.tsx     # Copy, Navigate, Rollback
│   └── DockablePanel/
│       ├── DockableContainer.tsx # Resize/dock management
│       └── ResizeHandle.tsx      # Drag handle
└── hooks/
    ├── useDevConsole.ts          # Main Zustand store
    ├── useLogGrouping.ts         # Group logs by actionId
    └── useKeyboardShortcuts.ts   # Keyboard navigation
```

---

#### SmartPayloadViewer
Intelligent JSON viewer with automatic entity detection.

**Dependencies**:
```bash
npm install @uiw/react-json-view
```

**Features**:
1. **Auto-detect entities** in payload:
   - `assetId`, `asset_id` → Navigate to asset
   - `tag` matching `/^[A-Z]-\d+/` → Navigate to asset by tag
   - `ruleId`, `rule_id` → Navigate to rule
   - `cableId` → Navigate to cable

2. **Search in JSON**: Filter by keyword with highlighting

3. **Copy options**:
   - Copy single value (click on value)
   - Copy entire payload (button)
   - Smart formatting with indentation

4. **Expand/Collapse**:
   - Default: Collapse at level 2+
   - Expand All / Collapse All buttons

5. **Smart entity buttons**:
   - Detected entities shown as clickable buttons below viewer
   - Example: `[P-101 →] [M-102 →]`

**Usage**:
```tsx
<SmartPayloadViewer 
  data={log.context}
  onNavigate={(route) => navigate(route)}
/>
```

---

## Data Flow

### Log Creation Flow

```
User Action (Import)
  ↓
Backend Endpoint
  ↓
WorkflowEngine.start_workflow()
  ↓
ActionLogger.start_action() → WebSocket
  ↓
Frontend useDevConsole.addLog()
  ↓
Timeline renders workflow
```

### Real-time Updates

```
Backend: action_logger.log_step()
  ↓
WebSocketLogger.log()
  ↓
WebSocket broadcast
  ↓
Frontend: useDevConsole (Zustand)
  ↓
Timeline auto-updates (React)
```

---

## Filters

### Multi-Filter System

**Time**:
- ALL, 5M, 15M, 1H, 24H

**Level**:
- ALL, DEBUG, INFO, WARN, ERROR

**Topics** (multi-select):
- ASSETS, RULES, CABLES, IMPORT, AUTH, PROJECT, SYSTEM

**User**:
- MY (current user only)
- ALL (all users)

**Discipline** (multi-select):
- PROCESS, ELECTRICAL, AUTOMATION, MECHANICAL, PROJECT, PROCUREMENT

### Quick Presets

Pre-configured filter combinations:
- **My Recent Changes**: MY + 15M + (CREATE, UPDATE, DELETE)
- **Errors Only**: ERROR
- **Rule Executions**: RULES + RULE_EXECUTION
- **Current Session**: Session ID filter

---

## Status Indicators

### Visual Status

| Status | Color | Icon | Animation |
|--------|-------|------|-----------|
| RUNNING | Purple | ▶ | Pulse |
| COMPLETED | Green | ✓ | Solid |
| FAILED | Red | ✗ | Solid |
| PENDING | Gray | ⏸ | Dim |
| WARNING | Yellow | ⚠ | Attention |

### Progress Bars

- **Workflow**: Overall progress across all jobs
- **Job**: Individual job progress
- Smooth animations (no jumps)
- Real-time updates via WebSocket

---

## User Modes

### User Mode (Default)
**For**: End users (engineers, project managers)

**Shows**:
- Only user-initiated actions
- Simplified messages
- Hide DEBUG, SYSTEM logs (except errors)
- Hide NETWORK logs (except errors)

**UI**:
- Workflows collapsed by default
- Show only summary stats
- Click to expand for details

---

### Dev Mode
**For**: Developers, debugging

**Shows**:
- ALL logs (DEBUG, SYSTEM, NETWORK)
- Raw payloads
- Performance metrics
- Stack traces

**UI**:
- Running workflows expanded
- Show all technical details
- Raw logs option

**Toggle**: Button in header `[🔧 Dev] / [👤 User]`

---

## Dockable Panel

### Positions
- **Bottom**: Default, horizontal layout
- **Right**: Vertical layout
- **Left**: Vertical layout (alternative)
- **Floating**: Detached window (future)

### Resize
- Drag handle at panel edge
- Min size: 150px (bottom), 300px (right/left)
- Max size: 90% of viewport
- App layout adjusts automatically

### Persistence
- Position and size saved to `localStorage`
- Restored on next session

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl + \` | Toggle DevConsole |
| `↑ / ↓` | Navigate timeline |
| `Enter` | Expand/select workflow |
| `c` | Copy selected log |
| `Esc` | Clear selection |
| `/` | Focus search |

---

## Export Options

### Copy
- **Single log**: Plain text format
- **All visible**: Respects current filters
- **JSON format**: Pretty-printed with indentation

### Export
- **CSV**: Time, Level, Message, Entity (Excel-compatible)
- **JSON**: Full log structure with context

---

## Performance

### Implemented Optimizations

1. **Log Pruning**: Automatic limit of 1000 logs in memory
   - Oldest logs removed when limit exceeded
   - Prevents memory bloat during long sessions
2. **Filter Memoization**: `useMemo` for expensive filtering operations
   - Prevents unnecessary re-calculations
   - Improves filter response time
3. **Auto-scroll Management**: Smart scroll behavior
   - Auto-scrolls to bottom when new logs arrive
   - Disables on manual scroll up
   - "Scroll to bottom" button appears when not at bottom
4. **WebSocket Throttle**: Max 10 updates/second
5. **React Optimizations**: Built-in virtual DOM diffing handles rendering efficiently

### Performance Targets
- Target: < 16ms render time (60 FPS)
- Memory: < 50MB for 1000 logs
- WebSocket: < 100ms latency

### Future Optimizations (Deferred)
- **Virtual Scrolling**: Not implemented - current log volume (< 1000) renders efficiently without it
- **Lazy Rendering**: React's built-in optimizations handle this adequately

---

## UX Polish Features

### Auto-scroll Intelligence
- Automatically scrolls to newest logs
- Preserves scroll position when user scrolls up (reading older logs)
- Floating "Scroll to bottom" button (↓) when not at bottom
- Re-enables auto-scroll when user manually scrolls to bottom

### Visual Feedback
- Smooth animations (slide-up panel entrance)
- Log count badge in header
- Connection status indicator (green/red WiFi icon)
- Real-time WebSocket connection status

### Keyboard Shortcuts
| Shortcut | Action |
|----------|--------|
| `Ctrl + \`` | Toggle DevConsole |
| `Ctrl + K` | Clear logs |
| `Ctrl + E` | Export logs |
| `Ctrl + C` | Copy selected log |
| `Esc` | Close panel |

---

## Integration with Existing Stack

### Loki/Grafana
DevConsole V3 **complements** Loki/Grafana:

**DevConsole**: 
- Real-time view during development
- User-facing activity feed
- Interactive navigation

**Grafana**:
- Historical analysis
- Production monitoring
- Alerts and dashboards

Both receive same logs via WebSocket → Loki.

---

## Migration Path

### Phase 1: Parallel Development
- Build DevConsoleV3 alongside old console
- Toggle via feature flag
- Test with subset of users

### Phase 2: Gradual Rollout
- Default to V3 for new users
- Keep V2 available (Ctrl+Shift+`)
- Collect feedback

### Phase 3: Full Migration
- Remove old DevConsole
- Update all documentation
- Archive V2 code

---

## API Reference

### Backend Endpoints

**Workflow Management**:
```
POST   /api/v1/workflows/          Create workflow
GET    /api/v1/workflows/{id}      Get workflow details
POST   /api/v1/workflows/{id}/jobs Create job in workflow
```

**WebSocket**:
```
WS     /ws/logs                    Real-time log stream
```

### Frontend Hooks

**useDevConsole**:
```typescript
const {
  filteredWorkflows,    // Grouped & filtered
  selectedLog,          // Currently selected
  setSelectedLog,       // Select log
  filters,              // Current filter state
  updateFilters,        // Update filters
} = useDevConsole();
```

---

## Troubleshooting

### WebSocket Disconnects
**Symptom**: Status shows "Offline"
**Fix**: Auto-reconnect after 3s, check backend logs

### Logs Not Grouping
**Symptom**: Logs appear flat, not hierarchical
**Fix**: Ensure `actionId` is set in backend logs

### Performance Issues
**Symptom**: UI lags with many logs
**Fix**: Enable virtual scrolling, reduce log retention (1000 → 500)

---

## Future Enhancements

- [ ] Workflow templates (user-defined)
- [ ] Custom presets (save filter combos)
- [ ] Export to PDF report
- [ ] Dark/Light theme toggle
- [ ] Floating window mode
- [ ] Collaborative debugging (share session)

---

**Last Updated**: 2025-11-24  
**Authors**: SYNAPSE Team  
**Related Docs**: 
- [Logging Infrastructure](./logging-infrastructure.md)
- [Workflow Engine](../developer-guide/workflow-engine.md)
