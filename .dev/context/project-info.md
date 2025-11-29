# Project Info (SSOT)

**Single source of truth for project configuration.**

---

## Repository

| Property | Value |
|----------|-------|
| **Name** | AXIOM |
| **URL** | https://github.com/seb155/AXIOM |
| **Branch principale** | master |
| **Type** | Monorepo |

## Applications

| App | Purpose | Port | Status |
|-----|---------|------|--------|
| **SYNAPSE** | MBSE Platform (FastAPI + React 19) | 4000 | MVP Dec 2025 |
| **NEXUS** | Knowledge Graph + Notes/Wiki | 5173 | Phase 1.5 |
| **PRISM** | Enterprise Dashboard | 5174 | Development |
| **ATLAS** | AI Collaboration Environment | 5175 | Planning |

**FORGE** = Shared infrastructure (PostgreSQL 5433, Redis 6379, Grafana 3000)

## Stack Technique

### Backend
- **Framework:** FastAPI
- **ORM:** SQLAlchemy
- **Migrations:** Alembic
- **Validation:** Pydantic
- **Tests:** pytest

### Frontend
- **Framework:** React 19
- **Language:** TypeScript (strict)
- **Build:** Vite
- **State:** Zustand
- **UI:** Shadcn/ui + Tailwind CSS

### Infrastructure
- **Containers:** Docker, docker-compose
- **Database:** PostgreSQL (port 5433)
- **Cache:** Redis (port 6379)
- **Proxy:** Traefik

## Naming Conventions

### Rule Names
- Format: `{SOURCE}: {Description}`
- Use spaces/colons, NEVER underscores
- Examples: `FIRM: Centrifugal Pumps require Electric Motor`

### Code
- **Python:** `snake_case` files, `PascalCase` classes
- **TypeScript:** `PascalCase.tsx` components, `camelCase.ts` utils
- **Database:** `plural_snake_case` tables

## Quick Start

```powershell
# Start everything
.\dev.ps1

# Or manually:
cd forge && docker compose up -d forge-postgres forge-redis
cd apps/synapse && docker compose -f docker-compose.dev.yml up --build
```

## Related Files

- Credentials: `.dev/context/credentials.md`
- Project State: `.dev/context/project-state.md`
- Test Status: `.dev/testing/test-status.md`

---

**Updated:** 2025-11-28
