# Rule Engine API Reference

**Version:** 1.0
**Base URL:** `/api/v1`

---

## Overview

The Rule Engine API provides endpoints for:
- **Rule Execution** - Execute rules with filters and real-time progress
- **Event Timeline** - Query workflow events with multi-criteria filtering
- **Asset History** - Track all changes to a specific asset
- **Rollback** - Undo batch executions

---

## Authentication

All endpoints require JWT authentication:

```http
Authorization: Bearer <token>
X-Project-ID: <project_id>
```

---

## Rule Execution

### Execute Rules

Execute rules on assets with optional filters.

```http
POST /api/v1/rules/execute
```

#### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `project_id` | string | Yes | Target project ID |
| `mode` | string | No | `"execute"` (default) or `"dry_run"` |
| `filters` | object | No | Execution filters |

##### Filters Object

| Field | Type | Description |
|-------|------|-------------|
| `rule_ids` | string[] | Execute only these rules |
| `disciplines` | string[] | Filter by discipline: `ELECTRICAL`, `AUTOMATION`, `MECHANICAL`, `PROCESS`, `PIPING`, `INSTRUMENTATION` |
| `action_types` | string[] | Filter by action: `CREATE_CHILD`, `CREATE_CABLE`, `SET_PROPERTY`, `CREATE_RELATIONSHIP`, `CREATE_PACKAGE`, `ALLOCATE_IO`, `VALIDATE` |
| `asset_ids` | string[] | Apply rules only to these assets |
| `asset_types` | string[] | Apply rules only to these asset types (e.g., `PUMP`, `MOTOR`) |

#### Request Example

```json
{
  "project_id": "proj-abc123",
  "mode": "execute",
  "filters": {
    "disciplines": ["ELECTRICAL"],
    "action_types": ["CREATE_CHILD", "CREATE_CABLE"],
    "asset_types": ["PUMP"]
  }
}
```

#### Response

```json
{
  "execution_id": "exec-xyz789",
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
  "ws_url": "/ws/execution/exec-xyz789",
  "status": "started"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `execution_id` | string | Unique execution identifier |
| `correlation_id` | uuid | Batch correlation ID for tracking/rollback |
| `ws_url` | string | WebSocket URL for real-time updates |
| `status` | string | `"started"` or `"preview"` (for dry_run) |

#### Status Codes

| Code | Description |
|------|-------------|
| 200 | Execution started |
| 400 | Invalid request (bad filters) |
| 401 | Unauthorized |
| 404 | Project not found |

---

### Dry Run (Preview)

Preview rule execution results without persisting changes.

```http
POST /api/v1/rules/execute
```

```json
{
  "project_id": "proj-abc123",
  "mode": "dry_run",
  "filters": {
    "disciplines": ["ELECTRICAL"]
  }
}
```

#### Dry Run Response

```json
{
  "execution_id": "exec-preview-123",
  "correlation_id": null,
  "ws_url": null,
  "status": "preview",
  "preview": {
    "total_rules": 5,
    "total_assets": 50,
    "actions": [
      {
        "rule_id": "rule-001",
        "rule_name": "Create Motor for Pumps",
        "asset_id": "asset-p101",
        "asset_tag": "P-101",
        "action_type": "CREATE_CHILD",
        "result": {
          "would_create": {
            "tag": "P-101-M",
            "type": "MOTOR"
          }
        }
      }
    ],
    "summary": {
      "creates": 15,
      "updates": 3,
      "skips": 32,
      "potential_conflicts": 2
    }
  }
}
```

---

### Rollback Execution

Undo a batch execution by restoring previous state.

```http
POST /api/v1/rules/rollback
```

#### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `correlation_id` | string (uuid) | Yes | Batch correlation ID to rollback |

#### Request Example

```json
{
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

#### Response

```json
{
  "status": "rolled_back",
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
  "rollback_correlation_id": "660f9500-f30c-52e5-b827-557766550000",
  "rolled_back_events": 45,
  "summary": {
    "assets_deleted": 15,
    "cables_deleted": 10,
    "edges_deleted": 15,
    "assets_restored": 5
  }
}
```

#### Status Codes

| Code | Description |
|------|-------------|
| 200 | Rollback successful |
| 400 | Invalid correlation_id or already rolled back |
| 401 | Unauthorized |
| 404 | Snapshot not found |

---

## Event Timeline

### Query Events

Query workflow events with multi-criteria filtering.

```http
GET /api/v1/events/timeline
```

#### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project_id` | string | Yes | Project ID |
| `asset_id` | string | No | Filter by asset |
| `rule_id` | string | No | Filter by rule |
| `discipline` | string | No | Filter by discipline |
| `event_types` | string | No | Comma-separated event types |
| `correlation_id` | string | No | Filter by batch |
| `from_date` | datetime | No | Start date (ISO 8601) |
| `to_date` | datetime | No | End date (ISO 8601) |
| `page` | int | No | Page number (default: 1) |
| `limit` | int | No | Items per page (default: 50, max: 100) |

#### Event Types

| Type | Description |
|------|-------------|
| `ASSET_CREATED` | New asset created |
| `ASSET_UPDATED` | Asset properties updated |
| `ASSET_DELETED` | Asset deleted |
| `CABLE_CREATED` | New cable created |
| `CABLE_UPDATED` | Cable properties updated |
| `CABLE_DELETED` | Cable deleted |
| `RELATIONSHIP_CREATED` | New edge/relationship created |
| `RELATIONSHIP_DELETED` | Edge deleted |
| `RULE_EXECUTION_STARTED` | Rule execution began |
| `RULE_EXECUTED` | Rule successfully applied |
| `RULE_SKIPPED` | Rule condition not met |
| `RULE_ERROR` | Rule execution failed |
| `RULE_EXECUTION_COMPLETED` | Rule execution finished |
| `BATCH_STARTED` | Batch execution started |
| `BATCH_COMPLETED` | Batch execution completed |
| `BATCH_ROLLED_BACK` | Batch was rolled back |
| `CSV_IMPORTED` | CSV data imported |
| `ROLLBACK` | Rollback event |

#### Request Example

```http
GET /api/v1/events/timeline
  ?project_id=proj-abc123
  &discipline=ELECTRICAL
  &event_types=ASSET_CREATED,CABLE_CREATED
  &from_date=2025-11-01T00:00:00Z
  &to_date=2025-11-30T23:59:59Z
  &page=1
  &limit=50
```

#### Response

```json
{
  "events": [
    {
      "id": "evt-001",
      "event_type": "ASSET_CREATED",
      "aggregate_type": "ASSET",
      "aggregate_id": "asset-motor-001",
      "payload": {
        "after": {
          "tag": "P-101-M",
          "type": "MOTOR",
          "properties": {
            "hp": 50,
            "voltage": "600V"
          }
        },
        "context": {
          "rule_name": "Create Motor for Pumps",
          "parent_asset": "P-101"
        }
      },
      "rule_id": "rule-001",
      "discipline": "ELECTRICAL",
      "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
      "timestamp": "2025-11-28T14:32:01Z",
      "is_rolled_back": false
    }
  ],
  "total": 150,
  "page": 1,
  "pages": 3
}
```

---

### Get Asset History

Get complete event history for a specific asset.

```http
GET /api/v1/events/assets/{asset_id}/history
```

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `asset_id` | string | Asset ID |

#### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project_id` | string | Yes | Project ID |

#### Response

```json
{
  "asset_id": "asset-p101",
  "asset_tag": "P-101",
  "history": [
    {
      "event_id": "evt-001",
      "event_type": "ASSET_CREATED",
      "timestamp": "2025-11-25T10:00:00Z",
      "source": "CSV_IMPORT",
      "user_id": "user-123",
      "changes": null,
      "snapshot": {
        "tag": "P-101",
        "type": "PUMP",
        "properties": {}
      }
    },
    {
      "event_id": "evt-002",
      "event_type": "ASSET_UPDATED",
      "timestamp": "2025-11-26T14:30:00Z",
      "source": "RULE",
      "rule_id": "rule-002",
      "rule_name": "Set Pump Properties",
      "changes": [
        {
          "field": "properties.hp",
          "old": null,
          "new": 50
        },
        {
          "field": "properties.voltage",
          "old": null,
          "new": "600V"
        }
      ]
    },
    {
      "event_id": "evt-003",
      "event_type": "RELATIONSHIP_CREATED",
      "timestamp": "2025-11-28T14:32:00Z",
      "source": "RULE",
      "rule_id": "rule-001",
      "rule_name": "Create Motor for Pumps",
      "related_entity": {
        "type": "ASSET",
        "id": "asset-motor-001",
        "tag": "P-101-M",
        "relation": "powers"
      }
    }
  ],
  "total_events": 3,
  "related_entities": [
    {
      "type": "MOTOR",
      "id": "asset-motor-001",
      "tag": "P-101-M",
      "relation": "child"
    },
    {
      "type": "CABLE",
      "id": "cable-001",
      "tag": "P-101-M-CBL",
      "relation": "connected"
    }
  ]
}
```

---

### Get Batch Events

Get all events for a specific execution batch.

```http
GET /api/v1/events/batch/{correlation_id}
```

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `correlation_id` | uuid | Batch correlation ID |

#### Response

```json
{
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
  "project_id": "proj-abc123",
  "executed_at": "2025-11-28T14:32:00Z",
  "executed_by": "user-123",
  "status": "ACTIVE",
  "events": [
    {
      "sequence_num": 0,
      "event_type": "BATCH_STARTED",
      "timestamp": "2025-11-28T14:32:00Z"
    },
    {
      "sequence_num": 1,
      "event_type": "RULE_EXECUTION_STARTED",
      "rule_name": "Create Motor for Pumps",
      "timestamp": "2025-11-28T14:32:00Z"
    }
  ],
  "summary": {
    "total_events": 47,
    "assets_created": 15,
    "cables_created": 10,
    "edges_created": 15,
    "assets_updated": 5,
    "errors": 0
  },
  "can_rollback": true
}
```

---

## WebSocket Protocol

### Connection

```javascript
const ws = new WebSocket('ws://host:8001/ws/execution/{execution_id}');
```

### Message Types (Server → Client)

#### STARTED

```json
{
  "type": "STARTED",
  "execution_id": "exec-xyz789",
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
  "total_rules": 15,
  "total_assets": 100,
  "filters_applied": {
    "disciplines": ["ELECTRICAL"],
    "asset_types": ["PUMP"]
  }
}
```

#### RULE_START

```json
{
  "type": "RULE_START",
  "rule_id": "rule-001",
  "rule_name": "Create Motor for Pumps",
  "discipline": "ELECTRICAL",
  "action_type": "CREATE_CHILD",
  "assets_to_process": 25,
  "progress": 10
}
```

#### ACTION

```json
{
  "type": "ACTION",
  "rule_id": "rule-001",
  "asset_id": "asset-p101",
  "asset_tag": "P-101",
  "action": "CREATED",
  "result": {
    "created_id": "asset-motor-001",
    "created_tag": "P-101-M",
    "created_type": "MOTOR"
  }
}
```

#### PROGRESS

```json
{
  "type": "PROGRESS",
  "progress": 65,
  "rules_completed": 10,
  "rules_total": 15,
  "actions_completed": 45,
  "actions_total": 75,
  "errors": 0,
  "elapsed_ms": 2500
}
```

#### RULE_COMPLETE

```json
{
  "type": "RULE_COMPLETE",
  "rule_id": "rule-001",
  "rule_name": "Create Motor for Pumps",
  "assets_processed": 25,
  "actions_taken": 20,
  "skipped": 5,
  "errors": 0,
  "duration_ms": 850
}
```

#### ERROR

```json
{
  "type": "ERROR",
  "rule_id": "rule-001",
  "asset_id": "asset-p102",
  "asset_tag": "P-102",
  "message": "Failed to create motor: duplicate tag P-102-M",
  "error_code": "DUPLICATE_TAG",
  "recoverable": true
}
```

#### COMPLETED

```json
{
  "type": "COMPLETED",
  "execution_id": "exec-xyz789",
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
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
    },
    "updated": {
      "assets": 10
    }
  }
}
```

### Message Types (Client → Server)

#### ping

```json
"ping"
```

Response: `"pong"`

#### cancel

```json
{
  "type": "cancel"
}
```

Response:
```json
{
  "type": "CANCELLED",
  "message": "Execution cancelled by user",
  "completed_actions": 45
}
```

---

## Error Responses

All endpoints return errors in this format:

```json
{
  "detail": "Error message describing what went wrong",
  "error_code": "ERROR_CODE",
  "context": {
    "field": "additional context"
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_PROJECT` | 404 | Project not found |
| `INVALID_CORRELATION` | 400 | Invalid correlation_id format |
| `ALREADY_ROLLED_BACK` | 400 | Batch already rolled back |
| `SNAPSHOT_NOT_FOUND` | 404 | No snapshot for correlation_id |
| `EXECUTION_IN_PROGRESS` | 409 | Another execution is running |
| `INVALID_FILTER` | 400 | Invalid filter parameter |

---

## Rate Limits

| Endpoint | Limit |
|----------|-------|
| `POST /rules/execute` | 10 req/min per project |
| `POST /rules/rollback` | 5 req/min per project |
| `GET /events/timeline` | 60 req/min |
| `WebSocket connections` | 5 concurrent per user |

---

## Examples

### cURL: Execute Rules

```bash
curl -X POST "http://localhost:8001/api/v1/rules/execute" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-Project-ID: proj-abc123" \
  -d '{
    "project_id": "proj-abc123",
    "mode": "execute",
    "filters": {
      "disciplines": ["ELECTRICAL"],
      "action_types": ["CREATE_CHILD"]
    }
  }'
```

### cURL: Query Timeline

```bash
curl "http://localhost:8001/api/v1/events/timeline?\
project_id=proj-abc123&\
discipline=ELECTRICAL&\
event_types=ASSET_CREATED,CABLE_CREATED&\
page=1&limit=50" \
  -H "Authorization: Bearer $TOKEN"
```

### cURL: Rollback

```bash
curl -X POST "http://localhost:8001/api/v1/rules/rollback" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-Project-ID: proj-abc123" \
  -d '{
    "correlation_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

### JavaScript: WebSocket

```javascript
const executionId = 'exec-xyz789';
const ws = new WebSocket(`ws://localhost:8001/ws/execution/${executionId}`);

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);

  switch (message.type) {
    case 'STARTED':
      console.log(`Executing ${message.total_rules} rules on ${message.total_assets} assets`);
      break;
    case 'PROGRESS':
      updateProgressBar(message.progress);
      break;
    case 'ACTION':
      addToLog(`${message.asset_tag} → ${message.result.created_tag}`);
      break;
    case 'COMPLETED':
      console.log(`Done! Created ${message.summary.created.assets} assets`);
      ws.close();
      break;
  }
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};
```

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-28 | Initial release |
