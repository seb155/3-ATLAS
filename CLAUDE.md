# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Platform Overview

**AXIOM** is the unified AXoiq development platform - a monorepo containing:

| App | Purpose | Port | Status |
|-----|---------|------|--------|
| **SYNAPSE** | MBSE Platform (FastAPI + React 19) | 4000 | MVP Dec 2025 |
| **NEXUS** | Knowledge Graph + Notes/Wiki | 5173 | Phase 1.5 |
| **PRISM** | Enterprise Dashboard | 5174 | Development |
| **ATLAS** | AI Collaboration Environment | 5175 | Planning |

**FORGE** = Shared infrastructure (PostgreSQL 5433, Redis 6379, Grafana 3000, Loki 3100)

---

## Quick Start

```powershell
# Start everything (FORGE + SYNAPSE)
.\dev.ps1

# Or start manually:
cd forge && docker compose up -d forge-postgres forge-redis
cd apps/synapse && docker compose -f docker-compose.dev.yml up --build

# Access: http://localhost:4000
# Login: admin@axoiq.com / admin123!
```

---

## Development Commands

### Backend (SYNAPSE - `apps/synapse/backend/`)

```bash
# Run server (inside container or locally)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Database migrations
alembic upgrade head
alembic revision --autogenerate -m "description"

# Tests
pytest                          # All tests
pytest -k "test_name"           # Single test by name
pytest tests/test_rules.py      # Single file
pytest --cov=app                # With coverage
pytest --cov=app --cov-report=html  # Coverage HTML report

# Linting
ruff check . --fix
```

### Frontend (SYNAPSE - `apps/synapse/frontend/`)

```bash
npm run dev                     # Dev server (port 4000)
npm run build                   # Production build
npm run test                    # Run tests
npm run test:watch              # Watch mode
npm run test:coverage           # Coverage report
npm run lint:fix                # Fix linting issues
npm run type-check              # TypeScript check
```

### Docker

```bash
docker logs synapse-backend -f --tail 100    # View logs
docker restart synapse-backend               # Restart service
docker exec -it forge-postgres psql -U postgres -d synapse  # DB shell
```

---

## Architecture

### SYNAPSE Backend (`apps/synapse/backend/app/`)

```
app/
├── main.py              # FastAPI app + exception handlers
├── api/endpoints/       # Route handlers (auth, assets, rules, ingestion, etc.)
├── services/            # Business logic
│   ├── rule_engine.py         # Rule execution engine
│   ├── cable_sizing.py        # Cable calculations
│   ├── ingestion_service.py   # CSV/Excel import
│   └── validation_service.py  # Data validation
├── models/              # SQLAlchemy ORM models
├── schemas/             # Pydantic request/response schemas
├── core/
│   ├── database.py      # DB connection + session
│   ├── config.py        # Settings (env vars)
│   ├── auth.py          # JWT authentication
│   └── exceptions.py    # Custom exception classes
└── scripts/             # Seed data + utilities
```

**Key API endpoints:**
- `/api/v1/auth/*` - Authentication (JWT)
- `/api/v1/projects/*` - Project management
- `/api/v1/assets/*` - Asset CRUD
- `/api/v1/rules/*` - Rule definitions
- `/api/v1/ingest/*` - CSV/Excel import

### Frontend Architecture

React 19 + TypeScript + Vite + Zustand (state) + React Router v6

---

## Naming Conventions

**Rule names:** Use spaces/colons, NEVER underscores
- ✅ `FIRM: Centrifugal Pumps require Electric Motor`
- ✅ `PROJECT-GoldMine: Use ABB Motors`
- ❌ `firm_motor_rule`

**Code:**
- Python: `snake_case` files, `PascalCase` classes, `snake_case` functions
- TypeScript: `PascalCase.tsx` components, `camelCase.ts` utils
- Database: `plural_snake_case` tables, `snake_case` columns

---

## FORGE Infrastructure

| Service | Container | Port |
|---------|-----------|------|
| PostgreSQL | `forge-postgres` | 5433 |
| Redis | `forge-redis` | 6379 |
| pgAdmin | `forge-pgadmin` | 5050 |
| Prisma Studio | `forge-prisma` | 5555 |
| Grafana | `forge-grafana` | 3000 |
| MeiliSearch | `forge-meilisearch` | 7700 |
| Docs (Docsify) | `forge-wiki` | 3080 |

---

## Session Start

At EVERY session start, load context:

```powershell
# Automated
.\.dev\scripts\smart-resume-enhanced.ps1

# Or manually read:
# 1. .dev/context/project-state.md    # Current MVP status
# 2. .dev/testing/test-status.md      # Test validation status
# 3. git status --short               # Uncommitted changes
```

**Related workflows:** `.agent/workflows/01-new-session.md`

---

## Key Files

| Need | File |
|------|------|
| Project state | `.dev/context/project-state.md` |
| Test tracking | `.dev/testing/test-status.md` |
| AI workflows | `.agent/workflows/` |
| Credentials | `.dev/context/credentials.md` |

---

## AI Agents System

### Orchestrators (Opus)

| Agent | Command | Purpose |
|-------|---------|---------|
| **ATLAS** | - | Main orchestrator, routes tasks to specialists |
| **BRAINSTORM** | `/brainstorm` | Creative sessions for specs |
| **SYSTEM-ARCHITECT** | `/system` | AI system governance (bypass) |
| **GENESIS** | `/genesis` | AI evolution & agent creation (bypass) |

### GENESIS - Meta-Agent

GENESIS est le meta-agent d'evolution du systeme. Il fonctionne en **bypass** (parallele a tous les autres agents).

```text
/genesis analyze    # Analyse sessions, identifie patterns
/genesis recommend  # Affiche recommandations en attente
/genesis create     # Cree drafts d'agents/skills/commands
/genesis benchmark  # Compare performances des agents
/genesis watch      # Veille technologique (web)
/genesis self       # Auto-amelioration
```

**Fichiers GENESIS:**
- `.claude/context/genesis-observations.md` - Recommandations
- `.claude/context/agent-metrics.md` - Metriques des agents
- `.claude/agents/drafts/` - Drafts en attente de validation

---

**Repository:** https://github.com/seb155/AXIOM
