# Plan de développement - Service plant3d-sync

> **Service:** plant3d-sync
> **Type:** Micro-service FastAPI
> **Objectif:** Synchronisation bidirectionnelle Plant3D ↔ SYNAPSE
> **Créé:** 2025-11-28

---

## 1. Vue d'ensemble

### Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          SYNAPSE Ecosystem                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────┐       ┌─────────────────────┐       ┌───────────┐ │
│  │   SYNAPSE   │       │    plant3d-sync     │       │  Plant3D  │ │
│  │   Backend   │◄─────►│    (FastAPI)        │◄─────►│  SQL DB   │ │
│  │   :8000     │  API  │    :8002            │  SQL  │           │ │
│  └──────┬──────┘       └──────────┬──────────┘       └───────────┘ │
│         │                         │                                 │
│         │              ┌──────────▼──────────┐                     │
│         │              │       Redis         │                     │
│         │              │   (Job Queue)       │                     │
│         │              │   :6379             │                     │
│         │              └─────────────────────┘                     │
│         │                                                          │
│  ┌──────▼──────┐                                                   │
│  │ PostgreSQL  │                                                   │
│  │  + pgvector │                                                   │
│  │   :5432     │                                                   │
│  └─────────────┘                                                   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Responsabilités

| Composant | Responsabilité |
|-----------|----------------|
| **plant3d-sync** | Lecture/écriture Plant3D DB, validation, résolution conflits |
| **SYNAPSE Backend** | API principale, logique métier, stockage SYNAPSE |
| **Redis** | Queue de jobs, cache, retry logic |
| **PostgreSQL** | Données SYNAPSE, embeddings, audit |

---

## 2. Stack technique

```yaml
Framework: FastAPI 0.121+
Python: 3.10+
ORM: SQLAlchemy 2.0 (pour Plant3D SQL Server)
Driver SQL Server: pyodbc / pymssql
Queue: Redis + rq (ou celery)
Validation: Pydantic v2
Tests: pytest (>70% coverage)
Containerisation: Docker
```

---

## 3. Structure du projet

```
apps/
└── plant3d-sync/
    ├── Dockerfile
    ├── requirements.txt
    ├── requirements-dev.txt
    ├── pyproject.toml
    ├── alembic/                    # Migrations (tables internes)
    │   └── versions/
    ├── app/
    │   ├── __init__.py
    │   ├── main.py                 # FastAPI app
    │   ├── core/
    │   │   ├── config.py           # Settings (env vars)
    │   │   ├── security.py         # Auth avec SYNAPSE
    │   │   └── logging.py          # Structured logging
    │   ├── db/
    │   │   ├── plant3d.py          # Connexion SQL Server Plant3D
    │   │   ├── synapse.py          # Client API SYNAPSE
    │   │   └── redis.py            # Redis connection
    │   ├── models/
    │   │   ├── plant3d/            # Modèles Plant3D (lecture)
    │   │   │   ├── equipment.py
    │   │   │   ├── instrument.py
    │   │   │   ├── pipeline.py
    │   │   │   └── valve.py
    │   │   ├── synapse/            # Modèles SYNAPSE (mapping)
    │   │   │   └── asset.py
    │   │   └── sync.py             # Modèles internes (sync_log, conflicts)
    │   ├── schemas/
    │   │   ├── sync.py             # Pydantic schemas
    │   │   ├── conflict.py
    │   │   └── mapping.py
    │   ├── services/
    │   │   ├── sync_service.py     # Logique principale
    │   │   ├── mapper.py           # Plant3D ↔ SYNAPSE mapping
    │   │   ├── conflict_resolver.py
    │   │   ├── validator.py
    │   │   └── audit.py
    │   ├── api/
    │   │   ├── v1/
    │   │   │   ├── sync.py         # /sync endpoints
    │   │   │   ├── status.py       # /status endpoints
    │   │   │   └── conflicts.py    # /conflicts endpoints
    │   │   └── deps.py             # Dependencies
    │   └── workers/
    │       ├── sync_worker.py      # Background sync job
    │       └── scheduler.py        # Periodic sync (5 min)
    └── tests/
        ├── conftest.py
        ├── test_sync_service.py
        ├── test_mapper.py
        ├── test_conflict_resolver.py
        └── test_api/
```

---

## 4. API Endpoints

### 4.1 Sync Operations

```yaml
POST /api/v1/sync/pull
  Description: Pull data from Plant3D to SYNAPSE
  Body:
    project_id: str
    entity_types: list[str]  # ["equipment", "instruments", "lines", "valves"]
    full_sync: bool = false  # true = all, false = changes since last sync
  Response:
    sync_id: str
    status: "queued" | "running" | "completed" | "failed"
    stats:
      total: int
      created: int
      updated: int
      skipped: int
      errors: int

POST /api/v1/sync/push
  Description: Push data from SYNAPSE to Plant3D
  Body:
    project_id: str
    asset_ids: list[str]  # specific assets, or empty for all modified
  Response:
    sync_id: str
    status: "queued" | "running" | "completed" | "failed"
    stats: {...}

POST /api/v1/sync/now
  Description: Immediate bidirectional sync (manual trigger)
  Body:
    project_id: str
  Response:
    sync_id: str
    pull_stats: {...}
    push_stats: {...}
```

### 4.2 Status & Monitoring

```yaml
GET /api/v1/sync/status
  Description: Get current sync status
  Query:
    project_id: str
  Response:
    last_sync: datetime
    next_scheduled: datetime
    current_job: {...} | null
    health: "healthy" | "degraded" | "offline"

GET /api/v1/sync/history
  Description: Sync history log
  Query:
    project_id: str
    limit: int = 50
    offset: int = 0
  Response:
    items: list[SyncLog]
    total: int

GET /api/v1/sync/{sync_id}
  Description: Get specific sync job details
  Response:
    sync_id: str
    status: str
    started_at: datetime
    completed_at: datetime | null
    stats: {...}
    errors: list[SyncError]
```

### 4.3 Conflict Management

```yaml
GET /api/v1/conflicts
  Description: List unresolved conflicts
  Query:
    project_id: str
    status: "pending" | "resolved" | "all"
  Response:
    items: list[Conflict]
    total: int

GET /api/v1/conflicts/{conflict_id}
  Description: Get conflict details
  Response:
    id: str
    asset_tag: str
    field: str
    plant3d_value: any
    synapse_value: any
    plant3d_updated_at: datetime
    synapse_updated_at: datetime
    suggested_resolution: str

POST /api/v1/conflicts/{conflict_id}/resolve
  Description: Resolve a conflict
  Body:
    resolution: "plant3d" | "synapse" | "manual"
    manual_value: any  # if resolution == "manual"
  Response:
    status: "resolved"
    applied_value: any
```

### 4.4 Health

```yaml
GET /health
  Description: Service health check
  Response:
    status: "healthy"
    plant3d_connection: "ok" | "error"
    synapse_connection: "ok" | "error"
    redis_connection: "ok" | "error"
    version: str
```

---

## 5. Data Mapping

### 5.1 Plant3D → SYNAPSE (Pull)

```python
# mapper.py

class Plant3DToSynapseMapper:
    """Maps Plant3D entities to SYNAPSE Asset format"""

    OWNERSHIP = {
        # Plant3D Master fields (read-only in SYNAPSE)
        "plant3d_master": [
            "tag", "asset_type", "asset_subtype",
            "line_number", "drawing_ref",
            "spec", "size", "rating", "range", "setpoint"
        ],
        # SYNAPSE Master fields (never overwritten by Plant3D)
        "synapse_master": [
            "fbs_code", "lbs_code", "wbs_code",
            "priority", "custom_tags", "m_files_links",
            "workflow_status", "notes", "embeddings"
        ],
        # Bidirectional (timestamp wins)
        "bidirectional": ["description"]
    }

    def map_equipment(self, plant3d_row: dict) -> AssetCreate:
        return AssetCreate(
            tag=plant3d_row["Tag"],
            description=plant3d_row["Description"],
            asset_type="Equipment",
            asset_subtype=plant3d_row["Class"],
            attributes={
                "spec": plant3d_row["Spec"],
                "size": plant3d_row["Size"],
                "rating": plant3d_row.get("Rating"),
            },
            plant3d_id=plant3d_row["ItemId"],
            plant3d_updated_at=plant3d_row["ModifiedDate"],
        )

    def map_instrument(self, plant3d_row: dict) -> AssetCreate:
        return AssetCreate(
            tag=plant3d_row["Tag"],
            description=plant3d_row["Description"],
            asset_type="Instrument",
            asset_subtype=self._extract_instrument_type(plant3d_row["Tag"]),
            attributes={
                "loop": plant3d_row.get("Loop"),
                "range": plant3d_row.get("Range"),
                "setpoint": plant3d_row.get("Setpoint"),
            },
            plant3d_id=plant3d_row["ItemId"],
            plant3d_updated_at=plant3d_row["ModifiedDate"],
        )

    def _extract_instrument_type(self, tag: str) -> str:
        """Extract type from tag: FT-1001 → FT (Flow Transmitter)"""
        prefix = tag.split("-")[0] if "-" in tag else tag[:2]
        return INSTRUMENT_TYPE_MAP.get(prefix, "Unknown")
```

### 5.2 SYNAPSE → Plant3D (Push)

```python
class SynapseToPlant3DMapper:
    """Maps SYNAPSE Asset to Plant3D format for push"""

    # Only push fields where SYNAPSE has authority
    PUSHABLE_FIELDS = ["description"]  # Bidirectional only

    def map_asset_to_equipment(self, asset: Asset) -> dict:
        return {
            "ItemId": asset.plant3d_id,
            "Description": asset.description,
            # Other fields are Plant3D master - don't push
        }
```

---

## 6. Conflict Resolution

### 6.1 Detection

```python
# conflict_resolver.py

class ConflictDetector:
    def detect(
        self,
        plant3d_data: dict,
        synapse_asset: Asset,
        field: str
    ) -> Conflict | None:
        """Detect if there's a conflict for a bidirectional field"""

        if field not in BIDIRECTIONAL_FIELDS:
            return None  # No conflict possible for owned fields

        plant3d_value = plant3d_data.get(field)
        synapse_value = getattr(synapse_asset, field)

        if plant3d_value == synapse_value:
            return None  # No conflict

        # Both changed since last sync
        if (plant3d_data["ModifiedDate"] > synapse_asset.last_sync_at and
            synapse_asset.updated_at > synapse_asset.last_sync_at):
            return Conflict(
                asset_id=synapse_asset.id,
                asset_tag=synapse_asset.tag,
                field=field,
                plant3d_value=plant3d_value,
                synapse_value=synapse_value,
                plant3d_updated_at=plant3d_data["ModifiedDate"],
                synapse_updated_at=synapse_asset.updated_at,
            )

        return None  # One side didn't change - auto-resolve
```

### 6.2 Auto-Resolution

```python
class ConflictResolver:
    def auto_resolve(self, conflict: Conflict) -> Resolution:
        """Auto-resolve based on timestamp for bidirectional fields"""

        if conflict.plant3d_updated_at > conflict.synapse_updated_at:
            return Resolution(
                winner="plant3d",
                value=conflict.plant3d_value
            )
        else:
            return Resolution(
                winner="synapse",
                value=conflict.synapse_value
            )

    def manual_resolve(
        self,
        conflict: Conflict,
        choice: str,
        manual_value: any = None
    ) -> Resolution:
        """Manual resolution by user"""

        if choice == "plant3d":
            return Resolution(winner="plant3d", value=conflict.plant3d_value)
        elif choice == "synapse":
            return Resolution(winner="synapse", value=conflict.synapse_value)
        elif choice == "manual":
            return Resolution(winner="manual", value=manual_value)
```

---

## 7. Background Jobs

### 7.1 Scheduled Sync

```python
# workers/scheduler.py

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.services.sync_service import SyncService

scheduler = AsyncIOScheduler()

@scheduler.scheduled_job('interval', minutes=5)
async def periodic_sync():
    """Run sync every 5 minutes for all active projects"""
    sync_service = SyncService()

    active_projects = await get_active_projects_with_plant3d()

    for project in active_projects:
        await sync_service.queue_sync(
            project_id=project.id,
            sync_type="incremental",
            direction="pull"
        )
```

### 7.2 Sync Worker

```python
# workers/sync_worker.py

from redis import Redis
from rq import Worker, Queue

redis_conn = Redis.from_url(settings.REDIS_URL)
queue = Queue("plant3d-sync", connection=redis_conn)

def process_sync_job(job_data: dict):
    """Process a sync job from the queue"""
    sync_service = SyncService()

    try:
        if job_data["direction"] == "pull":
            result = sync_service.pull_from_plant3d(
                project_id=job_data["project_id"],
                entity_types=job_data.get("entity_types", ["all"]),
                full_sync=job_data.get("full_sync", False)
            )
        elif job_data["direction"] == "push":
            result = sync_service.push_to_plant3d(
                project_id=job_data["project_id"],
                asset_ids=job_data.get("asset_ids", [])
            )

        return result

    except Exception as e:
        # Log error, update job status
        log_sync_error(job_data["sync_id"], e)
        raise
```

---

## 8. Configuration

### 8.1 Environment Variables

```bash
# .env.plant3d-sync

# Service
SERVICE_NAME=plant3d-sync
SERVICE_PORT=8002
DEBUG=false

# Plant3D SQL Server
PLANT3D_DB_HOST=localhost
PLANT3D_DB_PORT=1433
PLANT3D_DB_NAME=PnPDataLinks  # or actual DB name
PLANT3D_DB_USER=sa
PLANT3D_DB_PASSWORD=secret

# SYNAPSE API
SYNAPSE_API_URL=http://synapse-backend:8000
SYNAPSE_API_KEY=internal-service-key

# Redis
REDIS_URL=redis://forge-redis:6379/1

# Sync Settings
SYNC_INTERVAL_MINUTES=5
SYNC_BATCH_SIZE=500
SYNC_RETRY_ATTEMPTS=3
SYNC_RETRY_DELAY_SECONDS=30

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### 8.2 Docker Compose

```yaml
# docker-compose.dev.yml (addition)

services:
  plant3d-sync:
    build:
      context: ./apps/plant3d-sync
      dockerfile: Dockerfile
    container_name: plant3d-sync
    ports:
      - "8002:8002"
    environment:
      - PLANT3D_DB_HOST=${PLANT3D_DB_HOST}
      - PLANT3D_DB_PORT=${PLANT3D_DB_PORT}
      - PLANT3D_DB_NAME=${PLANT3D_DB_NAME}
      - PLANT3D_DB_USER=${PLANT3D_DB_USER}
      - PLANT3D_DB_PASSWORD=${PLANT3D_DB_PASSWORD}
      - SYNAPSE_API_URL=http://synapse-backend:8000
      - REDIS_URL=redis://forge-redis:6379/1
    depends_on:
      - forge-redis
      - synapse-backend
    networks:
      - forge-network
    restart: unless-stopped

  plant3d-sync-worker:
    build:
      context: ./apps/plant3d-sync
      dockerfile: Dockerfile
    container_name: plant3d-sync-worker
    command: python -m app.workers.sync_worker
    environment:
      - REDIS_URL=redis://forge-redis:6379/1
      - SYNAPSE_API_URL=http://synapse-backend:8000
    depends_on:
      - plant3d-sync
      - forge-redis
    networks:
      - forge-network
    restart: unless-stopped
```

---

## 9. Plan d'implémentation

### Phase 1: Foundation (Semaine 1)
- [ ] Setup projet FastAPI
- [ ] Connexion SQL Server Plant3D (lecture)
- [ ] Modèles Plant3D (Equipment, Instruments)
- [ ] Health endpoint
- [ ] Docker configuration
- [ ] Tests unitaires base

### Phase 2: Pull Sync (Semaine 2)
- [ ] Mapper Plant3D → SYNAPSE
- [ ] Service de sync (pull)
- [ ] Endpoint POST /sync/pull
- [ ] Intégration Redis queue
- [ ] Background worker
- [ ] Tests sync pull

### Phase 3: Push Sync (Semaine 3)
- [ ] Mapper SYNAPSE → Plant3D
- [ ] Service de sync (push)
- [ ] Endpoint POST /sync/push
- [ ] Gestion ownership (ne pas écraser Plant3D master)
- [ ] Tests sync push

### Phase 4: Conflicts & Polish (Semaine 4)
- [ ] Détection de conflits
- [ ] Résolution auto (timestamp)
- [ ] Endpoints /conflicts
- [ ] UI bouton "Sync Now" dans SYNAPSE
- [ ] Scheduler (5 min auto)
- [ ] Documentation API
- [ ] Tests intégration

---

## 10. Risques et mitigations

| Risque | Impact | Mitigation |
|--------|--------|------------|
| Schéma Plant3D inconnu | Haut | Analyser la DB avant dev, documenter |
| Corruption Plant3D | Critique | Transactions, backup avant push, mode read-only d'abord |
| Performance (gros volumes) | Moyen | Pagination, batch processing, indexes |
| Conflits fréquents | Moyen | Auto-resolve timestamp, notification UI |
| Plant3D offline | Faible | Queue Redis, retry logic, mode dégradé |

---

## 11. Questions ouvertes

- [ ] Nom exact de la base de données Plant3D
- [ ] Structure exacte des tables Plant3D (need schema dump)
- [ ] Authentification SQL Server (Windows Auth vs SQL Auth)
- [ ] Accès réseau au serveur Plant3D depuis Docker

---

**Document créé:** 2025-11-28
**Auteur:** Claude + Seb
**Version:** 1.0
