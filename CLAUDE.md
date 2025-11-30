# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## AI Orchestration

**ATLAS** is your main entry point - the orchestrator agent that manages all sessions and task routing.

**Start every session with:**
- `/0-new-session` - First session of the day (Mode FULL)
- `/0-next` - Continue next task (Mode QUICK)
- `/0-resume` - After /compact during development (Mode RECOVERY)

**See:** [.claude/agents/atlas.md](.claude/agents/atlas.md) for complete Atlas capabilities.

**Quick commands** (type `/0` to see all):
- `/0-progress` - Roadmap overview (compact)
- `/0-dashboard` - Current session status
- `/0-ship` - Git workflow (test + commit + push)

---

## Platform Overview

**AXIOM** is the unified AXoiq development platform with an AI OS at its core:

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
   └──────────┘         └──────────┘         └──────────┘
```

| App | Purpose | URL | Status |
|-----|---------|-----|--------|
| **ATLAS** | AI OS (contient CORTEX, Agents, ECHO) | - | ✅ Active |
| **CORTEX** | Memory Engine (CAG/RAG) - dans ATLAS | `https://cortex.axoiq.com` | 🚧 Dev |
| **APEX** | Enterprise Portal / Dashboard | `https://apex.axoiq.com` | 📋 Planning |
| **NEXUS** | Knowledge Portal + UI pour CORTEX | `https://nexus.axoiq.com` | 🏗️ Phase 2.0 |
| **SYNAPSE** | MBSE Platform (FastAPI + React 19) | `https://synapse.axoiq.com` | ✅ MVP Dec 2025 |

**FORGE** = Shared infrastructure via Traefik reverse proxy

**IMPORTANT:**
- **URLs Registry:** `.dev/infra/url-registry.yml` (SOURCE DE VÉRITÉ pour toutes les adresses)
- **Routing Rules:** `.claude/agents/rules/10-traefik-routing.md` (règles d'accès obligatoires)
- **Quick Reference:** `.dev/infra/QUICK-REFERENCE-URLS.md` (vue d'ensemble rapide)

---

## Quick Start

### Prérequis: Configurer le fichier hosts (une seule fois)

```powershell
# En tant qu'Administrateur
notepad C:\Windows\System32\drivers\etc\hosts
# Copier le contenu de: .dev\infra\hosts-entries.txt
```

### Démarrer les applications

```powershell
# 1. FORGE (Infrastructure + Traefik) - TOUJOURS EN PREMIER
cd D:\Projects\AXIOM\forge
docker compose -f docker-compose.yml -f docker-compose.traefik.yml up -d

# 2. SYNAPSE (avec labels Traefik)
cd D:\Projects\AXIOM\apps\synapse
docker compose -f docker-compose.dev.yml -f docker-compose.traefik-labels.yml up -d

# 3. NEXUS (avec labels Traefik)
cd D:\Projects\AXIOM\apps\nexus
docker compose -f docker-compose.dev.yml -f docker-compose.traefik-labels.yml up -d
```

### Accès (via noms de domaine)

**⚠️ TOUJOURS utiliser les noms de domaine, JAMAIS localhost:PORT**

| App | URL | Login |
|-----|-----|-------|
| **SYNAPSE** | https://synapse.axoiq.com | admin@aurumax.com / admin123! |
| **SYNAPSE API** | https://api.axoiq.com | - |
| **NEXUS** | https://nexus.axoiq.com | admin@aurumax.com / admin123! |
| **NEXUS API** | https://api-nexus.axoiq.com | - |
| **Grafana** | https://grafana.axoiq.com | admin / admin |
| **pgAdmin** | https://pgadmin.axoiq.com | admin@axoiq.com / admin |
| **Traefik** | https://traefik.axoiq.com | - |

**Personal Projects:**
| App | URL |
|-----|-----|
| **FinDash** | https://findash.axoiq.com |

**Voir:** `.dev/infra/QUICK-REFERENCE-URLS.md` pour la liste complète

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

### Demo Data Generation

**When database is empty and you need test data:**

```bash
# From backend directory
cd apps/synapse/backend
python -m app.scripts.seed_demo
```

**What it creates:**
- Admin user: `admin@aurumax.com` / `admin123!`
- 2 Clients: Goldmine Corp, Sandbox Inc
- 2 Projects: GoldMine Demo, Test Project
- 5 Baseline rules (FIRM + COUNTRY)
- 12 Demo assets (pumps, motors, transmitters, cables, etc.)
- 2 WBS Packages with assigned assets:
  - **PKG-IN-001** (Instrumentation, IN-P040 type) - 4 assets
  - **PKG-EL-001** (Electrical, CA-P040 type) - 3 assets

**Use cases:**
- Testing WBS Package View in Engineering Explorer
- Testing template export (IN-P040, CA-P040)
- Testing rule engine execution
- Any feature requiring sample data

**AI Agent Usage:** When you encounter an empty database during testing or development, run this script to populate complete demo data with packages for WBS testing.

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
| Traefik | `forge-traefik` | 80, 443, 8888 |

---

## Infrastructure Management System

**NEW (2025-11-28)**: Professional Infrastructure as Code system for managing AXIOM Docker infrastructure.

### ⚠️ MANDATORY POLICY FOR ALL AGENTS

**BEFORE any operation involving ports, networks, or Docker configuration:**

🔴 **YOU MUST READ THE INFRASTRUCTURE REGISTRY FIRST**

```
Read file: .dev/infra/registry.yml
```

**This applies to**:
- ✅ Adding new services or containers
- ✅ Allocating ports
- ✅ Configuring networks
- ✅ Modifying docker-compose files
- ✅ Diagnosing infrastructure issues
- ✅ Validating configurations

**DO NOT**:
- ❌ Guess port numbers
- ❌ Assume network configuration
- ❌ Create docker-compose without checking registry
- ❌ Modify infrastructure without consulting DevOps Manager

**Rule**: Registry is SINGLE SOURCE OF TRUTH. Read it first, ALWAYS.

### For AI Agents

**Quick Status (Read-Only)**:
```
skill: "infra"
```
Shows running services, port allocations, network health.

**Complex Operations (Diagnosis, Configuration, Validation)**:
```
Use Task tool with subagent_type="devops-manager"
```
Invokes intelligent Opus-powered DevOps Manager agent.

**When to use DevOps Manager**:
- Adding new services (port allocation, network configuration)
- Diagnosing infrastructure problems
- Validating docker-compose configurations
- Resolving port conflicts or network issues
- Major infrastructure changes

### For Developers (PowerShell CLI)

```powershell
# Quick status
.\.dev\scripts\axiom.ps1 status

# View port allocations
.\.dev\scripts\axiom.ps1 ports

# Start services
.\.dev\scripts\axiom.ps1 start synapse

# Validate infrastructure
.\.dev\scripts\axiom.ps1 validate

# Check health
.\.dev\scripts\axiom.ps1 health
```

### Port Allocation Ranges

| Application | Range | Allocated | Available |
|-------------|-------|-----------|-----------|
| **FORGE** | 3000-3999 | 9 ports | 991 ports |
| **SYNAPSE** | 4000-4999 | 2 ports | 998 ports |
| **NEXUS** | 5000-5999 | 2 ports | 998 ports |
| **APEX** | 6000-6999 | 0 ports | 1000 ports |
| **CORTEX** | 7000-7999 | 2 ports | 998 ports |

**Rule**: Each application has a dedicated 1000-port range. No conflicts allowed.

### Key Files

| File | Purpose | Used By |
|------|---------|---------|
| `.dev/infra/registry.yml` | Central registry (ports, services, networks) | DevOps Manager, validation |
| `.dev/infra/infrastructure.md` | Complete documentation | All agents, developers |
| `.dev/infra/CHANGELOG.md` | Change history | Tracking, rollback |
| `.claude/agents/devops-manager.md` | DevOps Manager agent (Opus) | Infrastructure orchestration |
| `.claude/skills/infra.md` | Infra skill (quick reference) | Status checking |

**See**:
- [.dev/infra/README.md](.dev/infra/README.md) - Complete Infrastructure Management System
- [.dev/infra/AGENT-QUICK-REFERENCE.md](.dev/infra/AGENT-QUICK-REFERENCE.md) - Quick reference for AI agents
- [docs/infrastructure/](docs/infrastructure/) - User documentation

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

### Implemented Agents

| Agent | File | Purpose |
|-------|------|---------|
| **ATLAS** | `.claude/agents/atlas.md` | Main orchestrator, routes tasks, manages context |
| **DevOps Manager** | `.claude/agents/devops-manager.md` | Infrastructure, Docker, ports, networks |
| **Brainstorm** | `.claude/agents/brainstorm.md` | Creative sessions, whiteboard mode |

### Slash Commands

| Command | Mode | Purpose |
|---------|------|---------|
| `/0-new-session` | FULL | Start new day with app review |
| `/0-next` | QUICK | Continue quickly without review |
| `/0-resume` | RECOVERY | Resume after interruption |
| `/0-ship` | - | Git workflow (test + commit + push) |
| `/0-progress` | - | View all apps progression |
| `/0-dashboard` | - | Current session status |

### Skills

| Skill | File | Purpose |
|-------|------|---------|
| `infra` | `.claude/skills/infra.md` | Quick infrastructure status |
| `brainstorm` | `.claude/skills/brainstorm.md` | Activate whiteboard mode |

### Hooks

| Hook | Type | Purpose |
|------|------|---------|
| Session Start | PreToolUse | Load context at startup |
| Pre-Commit | PreToolUse | Validate before commit |
| Context Update | PostToolUse | Update hot-files after edits |

### Agent Rules

| Rule | File | Purpose |
|------|------|---------|
| 10 | `10-traefik-routing.md` | Traefik routing rules |
| 11 | `11-url-registry.md` | URL management |
| 12 | `12-docker-networking.md` | Docker network config |
| 20 | `20-protected-docs.md` | Protected documents policy |

### ATLAS Development

For developing/improving ATLAS itself:
- `.atlas/CURRENT-STATE.md` - Current implementation state
- `.atlas/ROADMAP.md` - Development plan
- `.atlas/sessions/` - Session logs

---

## Status Line Pro

Le status line affiche en temps reel les informations de session Claude Code.

### Affichage

```
<< OPUS >> --- [ AXIOM/backend ] --- < master*3 > --- { A:1/2 } --- $0.42 --- 5m32s
```

| Section | Description |
|---------|-------------|
| `<< OPUS >>` | Modele actif (OPUS, SONNET, HAIKU) |
| `[ AXIOM/backend ]` | App + repertoire courant |
| `< master*3 >` | Branche git + fichiers modifies |
| `{ A:1/2 }` | Agents: running/total (optionnel) |
| `$0.42` | Cout de session USD |
| `5m32s` | Duree de session |

### Agent Tracking

Le badge `{ A:x/y }` affiche le nombre d'agents Task en cours d'execution.

**Fichier de status**: `.claude/context/agent-status.json`

```json
{
  "session_id": "2025-11-28-abc123",
  "agents": [
    {
      "id": "task-001",
      "name": "BACKEND-BUILDER",
      "task": "Create CSV endpoint",
      "status": "running",
      "started_at": "2025-11-28T10:30:00Z"
    }
  ],
  "summary": {
    "total": 2,
    "running": 1,
    "completed": 1,
    "failed": 0
  }
}
```

### Configuration

Fichiers:
- `.claude/scripts/statusline.ps1` - Script PowerShell
- `.claude/context/agent-status.json` - Status des agents Task
- `.claude/settings.json` - Configuration Claude Code

### Utilisation

**Activation automatique** - Le status line s'affiche des le demarrage de Claude Code.

**Restart requis** - Pour appliquer les changements, fermer et rouvrir Claude Code.

---

**Repository:** https://github.com/seb155/AXIOM
