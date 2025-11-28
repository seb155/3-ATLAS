# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> **AXIOM Platform** - AXoiq Enterprise Suite
> **Master Index:** `ATLAS.md` | **Context Index:** `.dev/index.md`

---

## Platform Overview

**AXIOM** is the unified AXoiq development platform containing:

| App | Purpose | Status |
|-----|---------|--------|
| **SYNAPSE** | MBSE Platform for EPCM Engineering | MVP Dec 20, 2025 |
| **NEXUS** | Personal Knowledge Graph + Notes/Wiki | Phase 1.5 |
| **PRISM** | Enterprise Portal / Dashboard | Development |
| **ATLAS** | AI Collaboration Environment | Planning |

**Infrastructure:** **FORGE** (shared workspace with PostgreSQL, Redis, Traefik, etc.)

---

## Project Structure

```
AXIOM/
├── apps/
│   ├── synapse/          # MBSE Platform (FastAPI + React 19)
│   ├── nexus/            # Knowledge Graph Portal
│   ├── prism/            # Enterprise Dashboard
│   └── atlas/            # AI Collaboration Env
│
├── forge/                # Shared Infrastructure
│   ├── docker-compose.yml
│   ├── config/
│   ├── databases/
│   └── scripts/
│
├── docs/                 # Documentation
├── .agent/               # AI Workflows
├── .dev/                 # Development Context
│
├── dev.ps1               # Start development
├── stop.ps1              # Stop all services
└── CLAUDE.md             # This file
```

---

## Technology Stack

### Backend (SYNAPSE)
- **Framework**: FastAPI 0.121+ (Python 3.10+)
- **Database**: PostgreSQL 15 via SQLAlchemy 2.0+
- **Migrations**: Alembic
- **Auth**: JWT (python-jose) + OAuth2
- **Testing**: pytest (>70% coverage target)
- **Linting**: Ruff + Black

### Frontend (All Apps)
- **Framework**: React 19 + TypeScript (strict mode)
- **Build**: Vite 7.2+
- **State**: Zustand
- **UI**: Shadcn/ui + Radix UI + Tailwind CSS
- **Router**: React Router v6
- **HTTP**: Axios (with interceptors)

### Infrastructure (FORGE)
- **Containerization**: Docker Compose
- **Database**: PostgreSQL 15 (forge-postgres)
- **Cache**: Redis 7 (forge-redis)
- **Logging**: Loki + Grafana + Promtail
- **Proxy**: Traefik

---

## Quick Start

### Prerequisites
```powershell
# 1. Start FORGE infrastructure FIRST
cd forge
docker compose up -d forge-postgres forge-redis

# Wait for PostgreSQL to be healthy
docker ps --filter "name=postgres"  # Should show "healthy"
```

### Start Applications
```powershell
# Option 1: Start SYNAPSE (primary app)
.\dev.ps1

# Option 2: Start specific app
cd apps/synapse
docker compose -f docker-compose.dev.yml up --build
```

**Default Credentials:**
- Email: `admin@axoiq.com`
- Password: `admin123!`

---

## Applications

### SYNAPSE - MBSE Platform
**Path:** `apps/synapse/`
**Purpose:** Model-Based Systems Engineering for EPCM Automation
**Status:** MVP (Dec 20, 2025)

```powershell
cd apps/synapse
docker compose -f docker-compose.dev.yml up --build
# Access: http://localhost:4000
```

### NEXUS - Knowledge Graph
**Path:** `apps/nexus/`
**Purpose:** Personal/Team Knowledge Graph + Notes + Wiki + Tasks
**Status:** Phase 1.5 (Visual Polish)

```powershell
cd apps/nexus
.\dev.ps1
# Access: http://localhost:5173
```

### PRISM - Enterprise Portal
**Path:** `apps/prism/`
**Purpose:** Enterprise Dashboard / Project Portal
**Status:** Development

### ATLAS - AI Collaboration
**Path:** `apps/atlas/`
**Purpose:** AI-assisted development environment
**Status:** Planning

---

## Development Commands

### Backend (FastAPI)
```bash
cd apps/synapse/backend

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Database migrations
alembic upgrade head
alembic revision --autogenerate -m "description"

# Run tests
pytest --cov=app
```

### Frontend (React + Vite)
```bash
cd apps/synapse/frontend

# Install dependencies
npm install

# Development server
npm run dev

# Testing
npm run test
npm run test:coverage
```

### Docker Commands
```bash
# View logs
docker logs synapse-backend --tail 50 -f

# Restart services
docker restart synapse-backend

# Access database
docker exec -it forge-postgres psql -U postgres -d synapse
```

---

## Session Start

**Use `/01-new-session` workflow at EVERY session start**

### Quick Start
```powershell
.\.dev\scripts\smart-resume-enhanced.ps1
```

### Manual Start
Read `.agent/workflows/01-new-session.md`

---

## Navigation

| Need | File |
|------|------|
| **Session start** | `.agent/workflows/01-new-session.md` |
| **AI system docs** | `00_AGENT_START.md` |
| **Current state** | `.dev/context/project-state.md` |
| **Test tracking** | `.dev/testing/test-status.md` |
| Credentials | `.dev/context/credentials.md` |

---

**Version:** v1.0.0 | **MVP Target:** Dec 20, 2025
**Platform:** AXIOM by AXoiq

## FORGE Services

| Service | Container | Port | URL |
|---------|-----------|------|-----|
| PostgreSQL | `forge-postgres` | 5433 | - |
| Redis | `forge-redis` | 6379 | - |
| pgAdmin | `forge-pgadmin` | 5050 | http://localhost:5050 |
| Prisma Studio | `forge-prisma` | 5555 | http://localhost:5555 |
| Grafana | `forge-grafana` | 3000 | http://localhost:3000 |
| Loki | `forge-loki` | 3100 | http://localhost:3100 |
| MeiliSearch | `forge-meilisearch` | 7700 | http://localhost:7700 |
| Wiki | `forge-wiki` | 3080 | http://localhost:3080 |

---

## Migration History (2025-11-28)

This repository was created by consolidating multiple projects:

| Original | New Location | Notes |
|----------|--------------|-------|
| EPCB-Tools | AXIOM/ | Monorepo root |
| EPCB-Tools/apps/synapse | apps/synapse/ | Unchanged |
| nexus/ (separate repo) | apps/nexus/ | Integrated |
| EPCB-Tools/apps/portal | apps/prism/ | Renamed |
| EPCB-Tools/workspace | forge/ | Renamed |
| (new) | apps/atlas/ | Created |

Infrastructure renamed: `workspace-*` → `forge-*`

See `docs/MIGRATION-AXIOM.md` for full details.

---

**Repository:** https://github.com/seb155/AXIOM

---

## Documentation

Documentation is served via **Docsify** at http://localhost:3080

**Local files:** `docs/` directory (edit Markdown files directly)

| Documentation | Path |
|---------------|------|
| Platform Overview | `docs/README.md` |
| Migration Guide | `docs/MIGRATION-AXIOM.md` |
| SYNAPSE docs | `docs/apps/synapse.md` |
| NEXUS docs | `docs/apps/nexus.md` |
| PRISM docs | `docs/apps/prism.md` |
| ATLAS docs | `docs/apps/atlas.md` |
| Getting Started | `docs/getting-started/` |
| Developer Guide | `docs/developer-guide/` |
| Reference | `docs/reference/` |
