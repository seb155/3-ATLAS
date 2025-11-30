# Architecture Overview

> Understand AXIOM's architecture in 5 minutes.

---

## Platform Overview

**AXIOM** is a unified monorepo platform containing 4 applications sharing common infrastructure.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AXIOM PLATFORM                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │   SYNAPSE   │ │    NEXUS    │ │    APEX     │ │    ATLAS    │           │
│  │  Port 4000  │ │  Port 5173  │ │  Port 6000  │ │   (AI OS)   │           │
│  │ MBSE Engine │ │Knowledge Mgmt│ │  Dashboard  │ │Contains CORTEX│         │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └──────┬──────┘           │
│         │               │               │               │                   │
│         └───────────────┴───────────────┴───────────────┘                   │
│                                   │                                         │
│                          ┌────────▼────────┐                                │
│                          │  forge-network  │                                │
│                          └────────┬────────┘                                │
│                                   │                                         │
│  ┌────────────────────────────────┴────────────────────────────────────┐   │
│  │                        FORGE INFRASTRUCTURE                          │   │
│  │    PostgreSQL │ Redis │ Loki │ Grafana │ MeiliSearch │ Traefik      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Applications

| App | Port | Description | Status |
|:---|:---:|:---|:---:|
| **SYNAPSE** | 4000 | MBSE Platform - Engineering automation | MVP v0.2.5 |
| **NEXUS** | 5173 | Knowledge Graph - Notes, Wiki, Tasks | Phase 1.5 |
| **APEX** | 6000 | Enterprise Portal - Dashboard & App Launcher | Planning |
| **ATLAS** | - | AI OS (contains CORTEX, Agents, ECHO) | Active |

---

## Project Structure

```
AXIOM/
├── apps/                        # Applications
│   ├── synapse/                 # MBSE Platform
│   │   ├── backend/app/         #   FastAPI backend
│   │   └── frontend/src/        #   React 19 frontend
│   ├── nexus/                   # Knowledge Graph
│   ├── apex/                    # Enterprise Portal (planning)
│   ├── atlas/                   # AI OS
│   └── cortex/                  # Memory Engine (in ATLAS)
│
├── forge/                       # Shared Infrastructure
│   └── docker-compose.yml       #   All shared services
│
├── .claude/                     # AI Agents System
│   ├── agents/                  #   18+ specialized agents
│   └── commands/                #   Slash commands
│
├── .dev/                        # Development Tracking
│   ├── ARCHITECTURE.md          #   Full architecture reference
│   ├── context/                 #   Project state
│   └── infra/registry.yml       #   Port registry (CRITICAL)
│
├── docs/                        # This documentation
├── CLAUDE.md                    # AI Instructions
└── README.md                    # GitHub README
```

---

## SYNAPSE Architecture

**SYNAPSE** = MBSE Platform for EPCM Automation

### Data Flow

```
CSV/Excel Import → Ingestion Service → Assets (PostgreSQL)
                                           ↓
                                      Rule Engine
                                           ↓
                            Complete Assets + Cables + Packages
                                           ↓
                                    Template Export
                               (IN-P040, CA-P040 Excel)
```

### Backend Stack

| Technology | Purpose |
|:---|:---|
| FastAPI | Web framework |
| SQLAlchemy | ORM |
| PostgreSQL | Database |
| Pydantic | Validation |
| Alembic | Migrations |

### Frontend Stack

| Technology | Purpose |
|:---|:---|
| React 19 | UI Framework |
| TypeScript | Type safety |
| Vite | Build tool |
| Zustand | State management |
| TailwindCSS | Styling |
| shadcn/ui | Components |

### Key Features

| Feature | Description |
|:---|:---|
| **Rule Engine** | 3 action types: CREATE_CHILD, CREATE_CABLE, CREATE_PACKAGE |
| **Workflow Audit** | Complete event sourcing with versioning |
| **Template Export** | IN-P040 (Instrument Index), CA-P040 (Cable Schedule) |
| **Full-text Search** | MeiliSearch integration |
| **Real-time Logs** | WebSocket DevConsole |

---

## FORGE Infrastructure

Shared services available to all applications:

| Service | Container | Port | Purpose |
|:---|:---|:---:|:---|
| **PostgreSQL** | `forge-postgres` | 5433 | Primary database |
| **Redis** | `forge-redis` | 6379 | Cache & sessions |
| **Loki** | `forge-loki` | 3100 | Log aggregation |
| **Grafana** | `forge-grafana` | 3000 | Monitoring dashboards |
| **MeiliSearch** | `forge-meilisearch` | 7700 | Full-text search |
| **pgAdmin** | `forge-pgadmin` | 5050 | PostgreSQL GUI |
| **Prisma Studio** | `forge-prisma` | 5555 | Database browser |
| **Traefik** | `forge-traefik` | 80/443 | Reverse proxy |

### Port Allocation Strategy

Each application has a dedicated 1000-port range:

| Range | Application |
|:---|:---|
| 3000-3999 | FORGE infrastructure |
| 4000-4999 | SYNAPSE |
| 5000-5999 | NEXUS |
| 6000-6999 | APEX |
| 7000-7999 | CORTEX |

**Source of truth:** `.dev/infra/registry.yml`

---

## AI Agents System

AXIOM includes 18+ specialized AI agents for development:

```
ORCHESTRATORS (Opus)
├── ATLAS       - Main orchestrator, session management
├── GENESIS     - AI evolution, agent creation
├── BRAINSTORM  - Creative sessions
└── SYSTEM-ARCHITECT - Governance

SPECIALISTS
├── BUILDERS    - Backend, Frontend, DevOps, Architect, Integration
├── VALIDATORS  - QA-Tester, Issue-Reporter
├── TRACKERS    - Dev-Tracker, Git-Manager
└── PLANNERS    - Debugger, Planner, UX-Designer
```

### Quick Commands

| Command | Description |
|:---|:---|
| `/0-new-session` | Start new session (full context) |
| `/0-next` | Continue next task |
| `/0-progress` | View roadmap |
| `/0-ship` | Git workflow (test + commit + push) |

---

## Development vs Production

### Development (Current)

```
FORGE (shared)
├── PostgreSQL, Redis, Loki, Grafana, MeiliSearch
│
└── SYNAPSE connects via forge-network
    ├── backend:8001
    └── frontend:4000
```

**Start:** `.\dev.ps1`

### Production (Future)

Each application deploys standalone with its own infrastructure.

---

## Logging & Monitoring

Two parallel systems:

1. **Centralized (Loki + Grafana)** - Historical logs for analysis
2. **Real-time (WebSocket)** - Live logs in DevConsole

```
Backend → Promtail → Loki → Grafana (Dashboard)
    │
    └── WebSocket → DevConsole (Frontend)
```

**Access:**
- Grafana: http://localhost:3000
- DevConsole: `Ctrl+`` in frontend

---

## Next Steps

**For Users:**
- Start using: [First Steps](./02-first-steps.md)

**For Developers:**
- Deep dive: [Project Structure](../developer-guide/01-project-structure.md)
- Rule Engine: [Rule Engine Guide](../developer-guide/rule-engine-event-sourcing.md)
- Testing: [Testing Guide](../developer-guide/08-testing.md)

**Full Architecture:**
- Complete reference: [.dev/ARCHITECTURE.md](../../.dev/ARCHITECTURE.md)

---

*Last updated: 2025-11-29*
