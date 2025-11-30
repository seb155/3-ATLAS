<div align="center">

# AXIOM

### **The Unified Engineering & Knowledge Platform**

*Streamline your engineering workflows, centralize knowledge, and collaborate with AI*

[![Platform](https://img.shields.io/badge/Platform-AXIOM-blue?style=for-the-badge)](https://github.com/seb155/AXIOM)
[![Version](https://img.shields.io/badge/Version-0.2.5-green?style=for-the-badge)](./CHANGELOG.md)
[![License](https://img.shields.io/badge/License-Proprietary-red?style=for-the-badge)](#license)

[**Quick Start**](#-quick-start) · [**Architecture**](#-architecture) · [**Applications**](#-applications) · [**Documentation**](#-documentation)

---

</div>

## What is AXIOM?

**AXIOM** is an integrated enterprise platform that brings together engineering automation, knowledge management, and AI-powered development into a single, cohesive ecosystem.

### The Problem

- Engineering data scattered across Excel files, emails, and disconnected tools
- Knowledge trapped in silos - notes here, tasks there, documentation elsewhere
- Manual processes eating up valuable engineering time
- No traceability or audit trail for critical decisions

### The Solution

AXIOM provides **an integrated ecosystem** with an AI OS at its core:

```
┌────────────────────────────────────────────────────────────────┐
│                        ATLAS (AI OS)                           │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  CORTEX (Memory)  │  Agents  │  ECHO  │  Note_synch      │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
   ┌──────────┐         ┌──────────┐         ┌──────────┐
   │   APEX   │         │  NEXUS   │         │ SYNAPSE  │
   │ Portal   │         │ Knowledge│         │ App Eng  │
   │Enterprise│         │ Portal   │         │ MVP      │
   └──────────┘         └──────────┘         └──────────┘
```

| | App | Purpose | Status |
|:---:|:---|:---|:---:|
| | [**ATLAS**](#-atlas---ai-os) | AI OS - Système central (contient CORTEX, Agents, ECHO) | Active |
| | [**APEX**](#-apex---enterprise-portal) | Portal enterprise - Dashboard & launcher | Planning |
| | [**NEXUS**](#-nexus---knowledge-portal) | Knowledge portal - Notes, wiki, graph 3D | Phase 2.0 |
| | [**SYNAPSE**](#-synapse---mbse-platform) | App ingénierie - Automatisation EPCM | MVP Dec 2025 |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AXIOM PLATFORM (Monorepo)                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                          ATLAS (AI OS)                                 │ │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐     │ │
│  │  │   CORTEX    │ │   Agents    │ │    ECHO     │ │ Note_synch  │     │ │
│  │  │  (Memory)   │ │(Claude Code)│ │  (Voice)    │ │  (Trilium)  │     │ │
│  │  │  CAG/RAG    │ │  ✅ Active  │ │  🚧 Dev     │ │  🏗️ Started │     │ │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘     │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│         │                       │                       │                   │
│         ▼                       ▼                       ▼                   │
│  ┌─────────────┐         ┌─────────────┐         ┌─────────────┐           │
│  │    APEX     │         │    NEXUS    │         │   SYNAPSE   │           │
│  │  Port 6000  │         │  Port 5173  │         │  Port 4000  │           │
│  │   Portal    │         │  Knowledge  │         │  MBSE App   │           │
│  │  📋 Plan    │         │  🏗️ Dev     │         │  ✅ MVP     │           │
│  └─────────────┘         └─────────────┘         └─────────────┘           │
│                                   │                                         │
│                          ┌────────▼────────┐                                │
│                          │  forge-network  │                                │
│                          └────────┬────────┘                                │
│                                   │                                         │
│  ┌────────────────────────────────┴────────────────────────────────────┐   │
│  │                        FORGE INFRASTRUCTURE                          │   │
│  │  ┌──────────┐ ┌────────┐ ┌────────┐ ┌───────┐ ┌─────────────────┐   │   │
│  │  │PostgreSQL│ │ Redis  │ │  Loki  │ │Grafana│ │   MeiliSearch   │   │   │
│  │  │  :5433   │ │ :6379  │ │ :3100  │ │ :3000 │ │      :7700      │   │   │
│  │  └──────────┘ └────────┘ └────────┘ └───────┘ └─────────────────┘   │   │
│  │  ┌──────────┐ ┌────────┐ ┌────────┐ ┌───────┐                       │   │
│  │  │ pgAdmin  │ │ Prisma │ │Traefik │ │  Wiki │                       │   │
│  │  │  :5050   │ │ :5555  │ │:80/443 │ │ :3080 │                       │   │
│  │  └──────────┘ └────────┘ └────────┘ └───────┘                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Project Structure

```
AXIOM/
├── apps/                        # Applications
│   ├── synapse/                 # MBSE Platform (FastAPI + React 19)
│   │   ├── backend/app/         #   API, services, models
│   │   └── frontend/src/        #   React components, pages
│   ├── nexus/                   # Knowledge Portal (Phase 2.0)
│   ├── apex/                    # Enterprise Portal (Planning)
│   ├── atlas/                   # AI OS (Active - contains CORTEX)
│   └── cortex/                  # Memory Engine (in ATLAS)
│
├── forge/                       # Shared Infrastructure
│   └── docker-compose.yml       #   PostgreSQL, Redis, Loki, Grafana...
│
├── .claude/                     # AI Agents System
│   ├── agents/                  #   18+ specialized agents
│   ├── commands/                #   Slash commands (/0-new-session, etc.)
│   └── skills/                  #   Reusable skills
│
├── .dev/                        # Development Tracking
│   ├── context/                 #   Project state, credentials
│   ├── infra/registry.yml       #   Port & service registry (CRITICAL)
│   ├── journal/                 #   Daily development logs
│   └── roadmap/                 #   Sprint planning
│
├── docs/                        # Public Documentation
├── CLAUDE.md                    # AI Instructions (read this!)
└── README.md                    # This file
```

---

## Quick Start

### Prerequisites

- [Docker Desktop](https://docker.com/products/docker-desktop) (required)
- [Node.js 20+](https://nodejs.org) (for frontend development)
- [Python 3.11+](https://python.org) (for backend development)
- PowerShell (Windows) or Bash (Linux/Mac)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/seb155/AXIOM.git
cd AXIOM

# 2. Start the platform (FORGE + SYNAPSE)
.\dev.ps1          # Windows PowerShell

# Or manually:
cd forge && docker compose up -d
cd apps/synapse && docker compose -f docker-compose.dev.yml up --build
```

### Access Applications

| Application | URL | Credentials |
|:---|:---|:---|
| **SYNAPSE** | [localhost:4000](http://localhost:4000) | `admin@axoiq.com` / `admin123!` |
| **Grafana** | [localhost:3000](http://localhost:3000) | `admin` / `admin` |
| **pgAdmin** | [localhost:5050](http://localhost:5050) | `admin@axiom.local` / `admin` |
| **Prisma Studio** | [localhost:5555](http://localhost:5555) | - |

### Generate Demo Data

```bash
cd apps/synapse/backend
python -m app.scripts.seed_demo
```

Creates: Admin user, 2 clients, 2 projects, 5 rules, 12 assets, 2 WBS packages.

---

## Applications

### SYNAPSE - MBSE Platform

> **Model-Based Systems Engineering for EPCM Projects**

Transform engineering data into deliverables automatically.

**Features:**
| Feature | Description |
|:---|:---|
| **Smart Import** | CSV/Excel ingestion with validation |
| **Rule Engine** | 3 action types: CREATE_CHILD, CREATE_CABLE, CREATE_PACKAGE |
| **Workflow Audit** | Complete event sourcing & traceability |
| **Template Export** | IN-P040 (Instrument Index), CA-P040 (Cable Schedule) |
| **Full-text Search** | MeiliSearch integration |
| **Real-time Logs** | WebSocket DevConsole |

**Tech Stack:** FastAPI + React 19 + TypeScript + PostgreSQL + Zustand

**Status:** MVP v0.2.5 (Target: December 2025)

---

### ATLAS - AI OS

> **The Intelligent Operating System**

ATLAS is the central nervous system of AXIOM. It's not just an app - it's the AI OS that powers everything.

**Contains:**
| Component | Status | Purpose |
|:---|:---:|:---|
| **CORTEX** | 🚧 Dev | Memory engine (CAG/RAG hybrid) |
| **Agents** | ✅ Active | Claude Code framework (18+ agents) |
| **ECHO** | 🚧 Dev | Voice → Transcription → Memory |
| **Note_synch** | 🏗️ Started | TriliumNext → Memory |

**Status:** Active (Agents system already running in Claude Code)

---

### APEX - Enterprise Portal

> **See Everything. Launch Anything.**

The enterprise dashboard and app launcher.

**Features:** App launcher, project metrics, team overview, health monitoring

**Status:** Planning

---

### NEXUS - Knowledge Portal

> **Your Second Brain**

Notes, wiki, tasks, and 3D knowledge graph visualization.

**Features:**
- Rich notes with TipTap editor
- Wiki with [[backlinks]]
- Kanban tasks
- 3D graph visualization (powered by CORTEX)
- Excalidraw whiteboard
- 13 themes

**Relationship with CORTEX:** NEXUS is the UI to visualize and interact with CORTEX's memory. It has its own data (notes, wiki) but also displays CORTEX's knowledge graph.

**Status:** Phase 2.0

---

## AI Agents System

AXIOM includes a complete **AI development assistant** with specialized agents:

```
┌─────────────────────── ORCHESTRATORS (Opus) ─────────────────────────┐
│  ATLAS (Main)  │  GENESIS (Meta)  │  BRAINSTORM  │  SYSTEM-ARCHITECT │
└──────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────── SPECIALISTS ──────────────────────────────────┐
│ BUILDERS          │ VALIDATORS      │ TRACKERS       │ PLANNERS      │
│ • Backend         │ • QA-Tester     │ • Dev-Tracker  │ • Debugger    │
│ • Frontend        │ • Issue-Reporter│ • Git-Manager  │ • Planner     │
│ • DevOps          │                 │                │ • UX-Designer │
│ • Architect       │                 │                │               │
│ • Integration     │                 │                │               │
└───────────────────────────────────────────────────────────────────────┘
```

### Quick Commands

```bash
/0-new-session    # Start new dev session (full context)
/0-next           # Continue next task (quick mode)
/0-resume         # Resume after /compact
/0-progress       # View roadmap progress
/0-dashboard      # Current session status
/0-ship           # Git workflow (test + commit + push)
```

See [AI Agents Guide](./docs/developer-guide/ai-agents-overview.md) for details.

---

## FORGE Infrastructure

Shared services for all applications:

| Service | Container | Port | Purpose |
|:---|:---|:---:|:---|
| **PostgreSQL** | `forge-postgres` | 5433 | Primary database |
| **Redis** | `forge-redis` | 6379 | Cache & sessions |
| **Loki** | `forge-loki` | 3100 | Log aggregation |
| **Grafana** | `forge-grafana` | 3000 | Monitoring dashboards |
| **MeiliSearch** | `forge-meilisearch` | 7700 | Full-text search |
| **pgAdmin** | `forge-pgadmin` | 5050 | PostgreSQL GUI |
| **Prisma Studio** | `forge-prisma` | 5555 | Database browser |
| **Traefik** | `forge-traefik` | 80/443 | Reverse proxy + SSL |
| **Wiki** | `forge-wiki` | 3080 | Documentation (Docsify) |

### Port Allocation

Each application has a dedicated 1000-port range:

| Range | Application | Allocated |
|:---|:---|:---:|
| 3000-3999 | FORGE | 9 ports |
| 4000-4999 | SYNAPSE | 2 ports |
| 5000-5999 | NEXUS | 2 ports |
| 6000-6999 | APEX | - |
| 7000-7999 | CORTEX | 2 ports |

**Registry:** `.dev/infra/registry.yml` (source of truth)

---

## Development

### Backend (SYNAPSE)

```bash
cd apps/synapse/backend

# Run server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Migrations
alembic upgrade head
alembic revision --autogenerate -m "description"

# Tests
pytest                          # All tests
pytest -k "test_name"           # Single test
pytest --cov=app                # With coverage

# Linting
ruff check . --fix
```

### Frontend (SYNAPSE)

```bash
cd apps/synapse/frontend

npm run dev                     # Dev server (port 4000)
npm run build                   # Production build
npm run test                    # Run tests
npm run lint:fix                # Fix linting
npm run type-check              # TypeScript check
```

### Docker Commands

```bash
docker logs synapse-backend -f --tail 100    # View logs
docker restart synapse-backend               # Restart
docker exec -it forge-postgres psql -U postgres -d synapse  # DB shell
```

---

## Documentation

### For New Users

| Document | Description |
|:---|:---|
| **[CLAUDE.md](./CLAUDE.md)** | AI assistant guide (START HERE) |
| **[Installation](./docs/getting-started/01-installation.md)** | Setup in 5 minutes |
| **[Architecture](./.dev/ARCHITECTURE.md)** | Complete system architecture |

### For Developers

| Document | Description |
|:---|:---|
| **[Project Structure](./docs/developer-guide/01-project-structure.md)** | Code organization |
| **[Rule Engine](./docs/developer-guide/rule-engine-event-sourcing.md)** | Rule engine deep dive |
| **[Testing](./docs/developer-guide/08-testing.md)** | Test guide |
| **[AI Agents](./docs/developer-guide/ai-agents-overview.md)** | Agent system |

### Internal (`.dev/`)

| Document | Description |
|:---|:---|
| **[.dev/README.md](./.dev/README.md)** | Development tracking index |
| **[.dev/ARCHITECTURE.md](./.dev/ARCHITECTURE.md)** | Full architecture reference |
| **[.dev/context/project-state.md](./.dev/context/project-state.md)** | Current MVP status |
| **[.dev/infra/registry.yml](./.dev/infra/registry.yml)** | Port & service registry |

---

## Roadmap

### Current Focus (Q4 2025)

- [x] SYNAPSE UI Foundation (VSCode-like shell)
- [x] CSV Import with validation
- [x] Rule Engine (CREATE_CHILD, CREATE_CABLE, CREATE_PACKAGE)
- [x] Workflow audit trail & versioning
- [x] Excel template export (IN-P040, CA-P040)
- [ ] Auto tests & CI/CD
- [ ] Demo preparation (December 20, 2025)

### Next (Q1 2026)

- [ ] NEXUS Phase 2 - Backend integration
- [ ] APEX initial release
- [ ] Multi-tenant improvements

### Future

- [ ] ATLAS AI Collaboration app
- [ ] Mobile companion
- [ ] Advanced AI integrations

---

## Technology Stack

| Layer | Technologies |
|:---|:---|
| **Frontend** | React 19, TypeScript, Vite, Zustand, TailwindCSS, shadcn/ui |
| **Backend** | FastAPI, Python 3.11, SQLAlchemy, Pydantic, Alembic |
| **Database** | PostgreSQL 15, Redis 7, MeiliSearch |
| **Infrastructure** | Docker Compose, Traefik, Loki, Grafana |
| **AI/Agents** | Claude (Opus/Sonnet/Haiku), 18+ specialized agents |

---

## Contributing

This is currently a private project. For access or collaboration inquiries, please contact the repository owner.

---

## License

**Proprietary** - All rights reserved.

---

<div align="center">

### Built with care by **AXoiq**

*Engineering the future, one platform at a time*

[![GitHub](https://img.shields.io/badge/GitHub-seb155-181717?style=flat-square&logo=github)](https://github.com/seb155)

</div>
