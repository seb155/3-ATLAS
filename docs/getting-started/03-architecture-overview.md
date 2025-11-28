# Architecture Overview

Understand SYNAPSE's architecture in 5 minutes.

---

## System Overview

**SYNAPSE** = MBSE Platform for EPCM Automation

**Input:** P&ID data (instruments, equipment)  
**Process:** Rule-based automation  
**Output:** Complete engineering deliverables (cables, IO lists, packages)

**Time Savings:** 320 hours → 20 hours per project (94% reduction)

---

## Monorepo Structure

```
EPCB-Tools/                      # Monorepo root
├── workspace/                   # Shared dev infrastructure
│   ├── PostgreSQL (5433)        # Database
│   ├── Prisma Studio (5555)     # DB GUI
│   ├── pgAdmin (5050)           # DB admin
│   ├── Redis (6379)             # Cache
│   ├── Loki (3100)              # Log aggregation
│   ├── Grafana (3000)           # Log visualization
│   └── Promtail                 # Log collector
│
└── apps/synapse/                # SYNAPSE application
    ├── backend/                 # FastAPI backend
    ├── frontend/                # React frontend
    └── docker-compose.dev.yml   # Dev config
```

**Why this structure?**
- ✅ **DEV:** Workspace shared by multiple projects (efficient)
- ✅ **PROD:** SYNAPSE deploys standalone (portable)
- ✅ **Clean:** Infrastructure vs application separation

---

## Technology Stack

**Frontend:**
- React 19, TypeScript
- TailwindCSS (styling)
- AG Grid (data tables)
- Zustand (state management)

**Backend:**
- FastAPI (Python 3.11+)
- SQLAlchemy (ORM)
- PostgreSQL 15 (database)

**Infrastructure:**
- Docker Compose (containers)
- Vite (dev server with hot-reload)
- Loki + Grafana (logging & monitoring)

**All open-source, no paid licenses.**

---

## Data Flow

```
┌─────────────┐
│ CSV/Excel   │
│ P&ID Data   │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│ Ingestion Service   │
│ Parse & Validate    │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Assets Table        │
│ (PostgreSQL)        │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Rule Engine         │
│ Auto-Complete       │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Complete Assets     │
│ Motors, Cables, IO  │
└─────────────────────┘
```

---

## Rule Engine

**Core concept:** Database-driven automation rules

**4-Tier Priority:**
```
CLIENT (100)   → Highest (client overrides)
PROJECT (50)   → Project-specific
COUNTRY (30)   → Regional standards (CEC, NEC)
FIRM (10)      → Baseline defaults
```

**6 Action Types:**
1. `CREATE_CHILD` - Create related asset (pump → motor)
2. `SET_PROPERTY` - Set properties (voltage = 600V)
3. `CREATE_CABLE` - Generate cables with sizing
4. `ALLOCATE_IO` - Assign PLC terminals
5. `CREATE_PACKAGE` - Group assets for deliverables
6. `VALIDATE` - Check engineering constraints

**Example:**
```
Rule: "Centrifugal Pumps require Electric Motor"
Condition: asset.type == "PUMP" AND asset.subtype == "CENTRIFUGAL"
Action: CREATE_CHILD(type="MOTOR", rated_power=asset.pump_power)
Priority: 10 (FIRM baseline)
```

---

## Multi-Tenancy

**Hierarchy:**
```
Clients
  └── Projects (isolated)
        └── Assets, Cables, Rules, Packages
```

**Isolation:** All data filtered by `project_id`

**Example:** AuruMax (client) has multiple projects:
- GoldMine Phase 1
- GoldMine Phase 2
- WaterPlant ABC

Each project has its own assets, rules don't cross projects.

---

## API Architecture

**Base URL:** `http://localhost:8001/api/v1/`

**Authentication:** JWT tokens

**Key Endpoints:**
- `/clients/` - Client management
- `/projects/` - Projects
- `/assets/` - Engineering assets
- `/cables/` - Generated cables
- `/rules/` - Automation rules

**Swagger UI:** http://localhost:8001/docs

---

## Logging & Monitoring

**Two parallel systems:**

1. **Centralized (Loki + Grafana)** - Historical logs for analysis
2. **Real-time (WebSocket)** - Live logs in DevConsole

```
Backend ──► Promtail ──► Loki ──► Grafana (Dashboard)
    │
    └──► WebSocket ──► DevConsole (Frontend)
```

**Access:**
- Grafana Dashboard: http://localhost:3000
- DevConsole: `Ctrl+\`` in frontend
- Logs API: http://localhost:8001/api/v1/logs/

**Details:** See [Logging Infrastructure](../reference/logging-infrastructure.md)

---

## Development vs Production

### Development (Current)

**Architecture:**
```
workspace/postgres  ← Shared DB
apps/synapse        ← Connects to workspace
```

**Start:** `.\dev.ps1`

**Benefits:** Fast, efficient, shared tools

### Production (Future - Proxmox)

**Architecture:**
```
apps/synapse/
  ├── db (dedicated PostgreSQL)
  ├── backend
  └── frontend
```

**Deploy:** Standalone docker-compose

**Benefits:** Isolated, scalable, portable

---

## Next Steps

**For users:**
- You understand the basics! Start using → [First Steps](02-first-steps.md)

**For developers:**
- Deep dive → [Project Structure](../developer-guide/01-project-structure.md)
- Backend guide → [Backend Guide](../developer-guide/02-backend-guide.md)
- Logging guide → [Logging Infrastructure](../reference/logging-infrastructure.md)
- Deploy guide → [Deployment](../developer-guide/06-deployment.md)

---

**Questions?** See [docs/README.md](../README.md) for full documentation index.
