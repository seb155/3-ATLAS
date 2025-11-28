# Logging Infrastructure

Complete guide to SYNAPSE's logging and monitoring system.

---

## Overview

SYNAPSE uses a dual logging architecture:

1. **Centralized Logging** (Loki + Grafana) - For historical analysis and monitoring
2. **Real-time Streaming** (WebSocket) - For DevConsole live view

```
                                    ┌─────────────┐
                                    │   Grafana   │
                                    │  Dashboard  │
                                    └──────▲──────┘
                                           │
┌─────────────┐    ┌─────────────┐   ┌─────┴─────┐
│   Backend   │───▶│  Promtail   │──▶│   Loki    │
│   (JSON)    │    │ (Collector) │   │  (Store)  │
└──────┬──────┘    └─────────────┘   └───────────┘
       │
       │ WebSocket
       ▼
┌─────────────┐
│  DevConsole │
│  (Frontend) │
└─────────────┘
```

---

## Access Points

| Service | URL | Credentials |
|---------|-----|-------------|
| Grafana | http://localhost:3000 | admin / (see credentials.md) |
| Loki API | http://localhost:3100/ready | - |
| DevConsole | Frontend `Ctrl+\`` | - |
| Logs HTTP | http://localhost:8001/api/v1/logs/ | - |

---

## Loki + Grafana Stack

### Services

**Loki** (port 3100)
- Log aggregation database
- Stores logs with labels for efficient querying
- Retention: 168 hours (7 days)

**Promtail**
- Collects logs from Docker containers
- Filters by label `logging=promtail`
- Extracts JSON fields (level, source, etc.)

**Grafana** (port 3000)
- Log visualization dashboard
- Pre-configured datasource and dashboard
- Auto-refresh every 5 seconds

### Configuration Files

```
workspace/config/
├── loki/
│   └── loki-config.yaml      # Loki server config
├── promtail/
│   └── promtail-config.yaml  # Log collection rules
└── grafana/
    └── provisioning/
        ├── datasources/
        │   └── datasources.yaml    # Loki datasource
        └── dashboards/
            ├── dashboards.yaml     # Dashboard provider
            └── synapse-logs.json   # SYNAPSE dashboard
```

### Grafana Dashboard

The "SYNAPSE Logs" dashboard includes:

| Panel | Type | Description |
|-------|------|-------------|
| Total Logs (1h) | Stat | Count of all logs |
| Errors (1h) | Stat | Error count (red) |
| Warnings (1h) | Stat | Warning count (yellow) |
| Write Operations | Stat | POST/PUT/DELETE count |
| Backend Logs | Logs | Full-text log viewer with search |
| Log Volume | Time series | Logs per interval |
| Logs by Level | Pie chart | Distribution by level |
| Errors Only | Logs | Filtered error view |

### LogQL Examples

```logql
# All backend logs
{job="synapse-backend"}

# Errors only
{job="synapse-backend"} |= "ERROR"

# Search for specific text
{job="synapse-backend"} |= "assets"

# Filter by HTTP method
{job="synapse-backend"} |~ "(POST|PUT|DELETE)"

# Count logs over time
count_over_time({job="synapse-backend"} [1h])
```

---

## WebSocket Real-time Logs

### Architecture

**Backend Components:**

```
LoggingMiddleware (middleware/)
    │
    ▼
WebSocketLogger (services/)
    ├── Store in memory (max 1000)
    ├── Print JSON to stdout (for Promtail)
    └── Broadcast to WebSocket clients
    │
    ▼
ConnectionManager
    └── Manage active WebSocket connections
```

**Endpoints:**

| Endpoint | Type | Description |
|----------|------|-------------|
| `/ws/logs` | WebSocket | Real-time log stream |
| `/api/v1/logs/` | GET | Fetch recent logs (HTTP fallback) |
| `/api/v1/logs/` | DELETE | Clear all logs |
| `/api/v1/logs/connections` | GET | Active WebSocket count |

### Log Entry Format

```json
{
  "id": "uuid",
  "timestamp": "2025-11-24T14:00:00.000000",
  "level": "INFO",
  "message": "GET /api/v1/assets/ → 200 (15ms)",
  "source": "BACKEND",
  "actionType": "RESPONSE",
  "context": {
    "request_id": "abc123",
    "status_code": 200,
    "duration_ms": 15.2,
    "method": "GET",
    "path": "/api/v1/assets/"
  },
  "status": "COMPLETED"
}
```

### Log Levels

| Level | Color | Usage |
|-------|-------|-------|
| DEBUG | Gray | Request start, verbose info |
| INFO | Blue | Successful responses |
| WARN | Yellow | 4xx errors (client errors) |
| ERROR | Red | 5xx errors, exceptions |

### WebSocket Commands

The WebSocket accepts text commands:

| Command | Response | Description |
|---------|----------|-------------|
| `ping` | `pong` | Keepalive check |
| `clear` | - | Clear server-side log buffer |

---

## Frontend Integration

### DevConsole Component

**Location:** `apps/synapse/frontend/src/components/DevConsole.tsx`

**Features:**
- Toggle with `Ctrl+\`` keyboard shortcut
- Live WebSocket status indicator (green/yellow/red)
- Tabs: Logs, Trace, Errors, Network
- Filters: Level (ALL/DEBUG/INFO/WARN/ERROR)
- Search: Full-text filter
- Export: Download logs as JSON

### Log Store

**Location:** `apps/synapse/frontend/src/store/useLogStore.ts`

```typescript
// Connect to WebSocket
const { connectWebSocket, disconnectWebSocket, wsState } = useLogStore();

// Get filtered logs
const logs = useLogStore(state => state.getFilteredLogs());

// Add a frontend log
useLogStore.getState().addLog({
  level: 'INFO',
  source: 'FRONTEND',
  message: 'User clicked button'
});
```

### WebSocket State

| State | Indicator | Description |
|-------|-----------|-------------|
| `connected` | Green | Active connection |
| `connecting` | Yellow (pulse) | Establishing connection |
| `disconnected` | Gray | Not connected |
| `error` | Red | Connection error |

Auto-reconnect attempts after 3 seconds on disconnect.

---

## Backend Integration

### Using WebSocketLogger

```python
from app.services.websocket_manager import WebSocketLogger

# Async context (endpoints)
await WebSocketLogger.log(
    level="INFO",
    message="Asset created",
    source="BACKEND",
    action_type="CREATE",
    entity_id="uuid",
    entity_type="Asset",
    discipline="AUTOMATION",
    context={"details": "..."}
)

# Sync context (non-async functions)
WebSocketLogger.log_sync(
    level="DEBUG",
    message="Processing started"
)
```

### LoggingMiddleware

Automatically logs all HTTP requests:

**Captured:**
- Request start (DEBUG)
- Response with status and timing (INFO/WARN/ERROR)
- Exceptions (ERROR)

**Skipped (noise reduction):**
- `/health` - Health checks
- `/ws/logs` - WebSocket upgrades
- `/docs`, `/openapi.json`, `/redoc` - API docs
- OPTIONS requests (CORS preflight)

---

## Troubleshooting

### Loki shows 404

**Normal behavior.** Loki has no web UI. Check `/ready`:
```bash
curl http://localhost:3100/ready
# Response: ready
```

### No logs in Grafana

1. Check Promtail is running:
   ```bash
   docker logs workspace-promtail --tail 20
   ```

2. Verify backend has `logging=promtail` label in docker-compose

3. Check Loki is receiving:
   ```bash
   curl "http://localhost:3100/loki/api/v1/query?query={job=\"synapse-backend\"}"
   ```

### WebSocket not connecting

1. Check backend is running:
   ```bash
   curl http://localhost:8001/health
   ```

2. Check connection count:
   ```bash
   curl http://localhost:8001/api/v1/logs/connections
   ```

3. Check browser console for WebSocket errors

### Logs not appearing in DevConsole

1. Open DevConsole (`Ctrl+\``)
2. Check status indicator (should be green)
3. Trigger an API call to generate logs
4. Check "ALL" level filter is selected

---

## Configuration

### Change Loki Retention

Edit `workspace/config/loki/loki-config.yaml`:
```yaml
limits_config:
  retention_period: 168h  # Change to desired duration
```

### Change Log Buffer Size

Edit `apps/synapse/backend/app/services/websocket_manager.py`:
```python
class WebSocketLogger:
    _max_logs = 1000  # Change to desired size
```

### Add Custom Dashboard Panel

Edit `workspace/config/grafana/provisioning/dashboards/synapse-logs.json`

Or create directly in Grafana UI (changes persist with `allowUiUpdates: true`)

---

**Related:**
- [Architecture Overview](../getting-started/03-architecture-overview.md)
- [Credentials](../../.dev/context/credentials.md)
- [Journal 2025-11-24](../../.dev/journal/2025-11/2025-11-24.md)
