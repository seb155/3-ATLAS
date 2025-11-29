# GEMINI.md

Instructions pour Google Antigravity / Gemini CLI dans le projet AXIOM.

## Context Files (Auto-imported)

@.dev/context/project-info.md
@.dev/context/credentials.md

## Platform Overview

**AXIOM** - Unified AXoiq development platform (monorepo)

| App | Purpose | Port |
|-----|---------|------|
| **SYNAPSE** | MBSE Platform (FastAPI + React 19) | 4000 |
| **NEXUS** | Knowledge Graph + Notes | 5173 |
| **PRISM** | Enterprise Dashboard | 5174 |
| **ATLAS** | AI Collaboration | 5175 |

**FORGE** = Shared infrastructure (PostgreSQL 5433, Redis 6379)

## Quick Start

```powershell
# Start everything
.\dev.ps1

# Access
# Frontend: http://localhost:4000
# API Docs: http://localhost:8001/docs
```

## Rules & Workflows

Rules and workflows are in `.agent/`:
- `.agent/rules/` - Mandatory conventions (always active)
- `.agent/workflows/` - Procedures triggered with `/`

**Available workflows:**
- `/00-start` - Quick session start
- `/00-onboarding` - New developer setup
- `/01-new-session` - Full context load
- `/02-database-migration` - Alembic migrations
- `/03-docker-troubleshoot` - Docker issues
- `/10-new-feature-mvp` - New feature workflow
- `/11-new-api-endpoint` - FastAPI endpoint
- `/12-new-react-component` - React component
- `/13-test-validation` - Run tests
- `/14-docker-rebuild` - Rebuild containers
- `/15-code-review` - Code review

## Development Commands

### Backend (apps/synapse/backend/)

```bash
# Server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Database
alembic upgrade head
alembic revision --autogenerate -m "description"

# Tests
pytest
pytest -k "test_name"
pytest --cov=app

# Linting
ruff check . --fix
```

### Frontend (apps/synapse/frontend/)

```bash
npm run dev          # Dev server (port 4000)
npm run build        # Production build
npm run test         # Run tests
npm run lint:fix     # Fix linting
npm run type-check   # TypeScript check
```

### Docker

```bash
docker logs synapse-backend -f --tail 100
docker restart synapse-backend
docker exec -it forge-postgres psql -U postgres -d synapse
```

## Key Conventions

### Rule Names
Use spaces/colons, NEVER underscores:
- `FIRM: Centrifugal Pumps require Electric Motor`
- `PROJECT-GoldMine: Use ABB Motors`

### Code Style
- **Python:** snake_case files, PascalCase classes
- **TypeScript:** PascalCase.tsx components, camelCase.ts utils
- **Database:** plural_snake_case tables

## Architecture

### Backend Structure
```
app/
├── main.py              # FastAPI app
├── api/endpoints/       # Route handlers
├── services/            # Business logic
├── models/              # SQLAlchemy models
├── schemas/             # Pydantic schemas
└── core/                # Config, auth, database
```

### Key Patterns
- Multi-tenancy: All models have `project_id`
- JWT authentication via `get_current_user`
- Pydantic schemas: Base, Create, Update, Response

## Session Start

At every session start:
1. Run `/00-start` for quick context
2. Or run `/01-new-session` for full context

## Related Documentation

- Project state: `.dev/context/project-state.md`
- Test status: `.dev/testing/test-status.md`
- Infrastructure: `.dev/infra/registry.yml`

---

**Repository:** https://github.com/seb155/AXIOM
