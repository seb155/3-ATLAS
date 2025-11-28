# Shared AI Context

**Common context for Claude Code and Gemini/Antigravity.**
**Single source of truth - referenced by CLAUDE.md and GEMINI.md**

---

## Project: SYNAPSE

**MBSE Platform for EPCM Automation**

| Metric | Value |
|--------|-------|
| Version | See `VERSION` file |
| Impact | 100 P&ID instruments -> 500+ assets (94% time saved) |
| Stack | FastAPI + React 19 + PostgreSQL 15 |

---

## Structure

```
EPCB-Tools/
├── workspace/              # Shared infra (Postgres, Prisma, Redis)
├── apps/synapse/
│   ├── backend/app/        # FastAPI (port 8001)
│   └── frontend/src/       # React (port 4000)
├── docs/                   # Documentation
│   ├── getting-started/
│   ├── developer-guide/
│   └── contributing/
├── .dev/                   # Dev tracking
│   ├── context/            # project-state.md <- READ FIRST
│   ├── journal/            # Daily logs
│   ├── decisions/          # ADR
│   └── roadmap/            # Sprints
└── .agent/                 # Antigravity rules/workflows
```

---

## Code Patterns

**Backend** (`apps/synapse/backend/app/`):
- Multi-tenancy: Always filter by `project_id`
- Type hints required
- Alembic for migrations (never raw SQL)

**Frontend** (`apps/synapse/frontend/src/`):
- TypeScript strict mode
- Zustand for state management
- TailwindCSS for styling

**Database:**
- PostgreSQL only (never SQLite)
- 12 core tables, 25+ API endpoints

---

## User Preferences

| Preference | Value |
|------------|-------|
| Language | FR/EN bilingual (tech in English) |
| Background | Senior Automation Engineer (PlantPAX, ControlLogix) |
| UI Style | No popups/modals (use pages, panels, inline) |
| Communication | Concise, direct |
| Analogies | Industrial (PLC, motor) NOT IT (shopping cart) |

---

## Navigation

| Need | File |
|------|------|
| Current state | `.dev/context/project-state.md` |
| Today's work | `.dev/journal/YYYY-MM/YYYY-MM-DD.md` |
| Sprint status | `.dev/roadmap/current-sprint.md` |
| Installation | `docs/getting-started/01-installation.md` |
| Architecture | `docs/getting-started/03-architecture-overview.md` |
| Code standards | `docs/contributing/code-guidelines.md` |

---

## Common Commands

```bash
# Docker
docker-compose -f apps/synapse/docker-compose.dev.yml up
docker-compose -f apps/synapse/docker-compose.dev.yml logs -f backend

# Database
docker exec synapse-backend-1 python -m app.scripts.seed_all
docker exec synapse-backend-1 alembic upgrade head
```

---

**Updated:** 2025-11-23
