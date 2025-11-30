# AXIOM Platform State

**Platform:** AXIOM - AXoiq Enterprise Suite
**Repository:** https://github.com/seb155/AXIOM
**Version:** v0.2.5
**Last Updated:** 2025-11-29

---

## Quick Reference

```
┌─────────────────────────────────────────────────────────────────┐
│                    AXIOM QUICK REFERENCE                        │
├─────────────────────────────────────────────────────────────────┤
│  START:        .\dev.ps1                                        │
│                                                                 │
│  URLS:                                                          │
│    SYNAPSE:    http://localhost:4000                            │
│    Grafana:    http://localhost:3000                            │
│    pgAdmin:    http://localhost:5050                            │
│    API Docs:   http://localhost:4000/api/v1/docs                │
│                                                                 │
│  CREDENTIALS:                                                   │
│    App:        admin@axoiq.com / admin123!                      │
│    Grafana:    admin / admin                                    │
│                                                                 │
│  COMMANDS:                                                      │
│    /0-new-session   Start new session (full context)            │
│    /0-next          Continue next task                          │
│    /0-ship          Git workflow (test + commit + push)         │
│                                                                 │
│  DEMO DATA:    python -m app.scripts.seed_demo                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Platform Overview

### Applications

| App | Port | Purpose | Status |
|:---|:---:|:---|:---:|
| **SYNAPSE** | 4000 | MBSE Platform - Engineering automation | MVP v0.2.5 |
| **NEXUS** | 5173 | Knowledge Graph - Notes, Wiki, Tasks | Phase 1.5 |
| **APEX** | 6000 | Enterprise Portal - Dashboard & App Launcher | Planning |
| **ATLAS** | - | AI OS (contains CORTEX, Agents, ECHO) | Active |

### Infrastructure (FORGE)

| Service | Port | Status |
|:---|:---:|:---:|
| PostgreSQL | 5433 | Active |
| Redis | 6379 | Active |
| Grafana | 3000 | Active |
| Loki | 3100 | Active |
| MeiliSearch | 7700 | Active |
| pgAdmin | 5050 | Active |
| Traefik | 80/443 | Active |

---

## Active Focus

### Primary: SYNAPSE MVP

**Version:** v0.2.5
**Target:** Demo-ready for December 20, 2025
**Sprint:** Week 4 - Auto Tests + CI/CD + Demo

**Completed Features:**
- [x] VSCode-like UI (Allotment panels)
- [x] CSV/Excel Import with validation
- [x] Rule Engine (CREATE_CHILD, CREATE_CABLE, CREATE_PACKAGE)
- [x] Workflow audit trail & versioning
- [x] Excel template export (IN-P040, CA-P040)
- [x] Package management system
- [x] WebSocket real-time logs
- [x] Full-text search (MeiliSearch)
- [x] AI Agents system (18+ agents)
- [x] Atlas orchestration system

**In Progress:**
- [ ] Auto tests & CI/CD
- [ ] Demo preparation

---

## Version History

| Version | Name | Date | Status |
|:---|:---|:---|:---:|
| v0.2.5 | Atlas Orchestration System | 2025-11-28 | ✅ |
| v0.2.4 | Templates & Package Export | 2025-11-28 | ✅ |
| v0.2.3 | MVP Backend Traceability | 2025-11-28 | ✅ |
| v0.2.2 | UX Professional + MVP Week 1 | 2025-11-27 | ✅ |
| v0.2.1 | Logging & Monitoring | 2025-11-24 | ✅ |
| v0.2.0 | Base Platform | 2025-11-23 | ✅ |

---

## Recent Changes

### 2025-11-29: Documentation Update
- Created `.dev/ARCHITECTURE.md` - Complete architecture reference
- Updated `README.md` - GitHub README with architecture diagrams
- Updated `.dev/README.md` - Development tracking index
- Updated `docs/README.md` - Documentation index
- Updated `docs/getting-started/03-architecture-overview.md`

### 2025-11-28: v0.2.5 - Atlas Orchestration System
**AI Session Management & Workflow Automation**

**New Files:**
- `.claude/agents/atlas.md` - Main orchestrator
- `.claude/commands/0-*.md` - Session commands
- `.claude/context/session-history.json` - Session tracking
- `.dev/context/task-queue.md` - Task management

**Commands Added:**
```
/0-new-session    # Full context load
/0-next           # Quick task resume
/0-resume         # Recovery after /compact
/0-progress       # Roadmap overview
/0-dashboard      # Session status
/0-ship           # Git workflow
```

### 2025-11-28: v0.2.4 - Templates & Package Export
**Package Generation System**

**New Files:**
- `app/services/template_service.py` - Excel generation
- `app/api/endpoints/packages.py` - Package CRUD
- `frontend/src/components/AssetHistory.tsx` - Version history UI

**Templates:**
- IN-P040: Instrument Index
- CA-P040: Cable Schedule

### 2025-11-28: v0.2.3 - Backend Traceability
**Event Sourcing & Audit Trail**

**New Files:**
- `app/services/workflow_logger.py` - Event sourcing
- `app/services/versioning_service.py` - Asset versioning
- `app/services/rule_execution_service.py` - Rule engine
- `app/models/workflow.py` - Workflow models

**Endpoints:**
```
GET  /api/v1/workflow/events
GET  /api/v1/workflow/timeline
GET  /api/v1/workflow/assets/{id}/versions
POST /api/v1/workflow/assets/{id}/rollback
```

---

## Architecture Summary

```
AXIOM/
├── apps/
│   ├── synapse/           # MBSE Platform (MVP)
│   │   ├── backend/       # FastAPI
│   │   └── frontend/      # React 19
│   ├── nexus/             # Knowledge Graph
│   ├── prism/             # Dashboard
│   └── atlas/             # AI Collab
├── forge/                 # Shared Infrastructure
├── .claude/               # AI Agents System
│   ├── agents/            # 18+ specialized agents
│   └── commands/          # Slash commands
├── .dev/                  # Development Tracking
│   ├── ARCHITECTURE.md    # Full architecture reference
│   ├── context/           # Project state
│   └── infra/registry.yml # Port registry
└── docs/                  # Documentation
```

**Full Architecture:** See [.dev/ARCHITECTURE.md](../ARCHITECTURE.md)

---

## Tech Stack

| Layer | Technologies |
|:---|:---|
| **Frontend** | React 19, TypeScript, Vite, Zustand, TailwindCSS |
| **Backend** | FastAPI, Python 3.11, SQLAlchemy, Pydantic |
| **Database** | PostgreSQL 15, Redis 7, MeiliSearch |
| **Infrastructure** | Docker Compose, Traefik, Loki, Grafana |
| **AI/Agents** | Claude (Opus/Sonnet/Haiku), 18+ agents |

---

## Key Files

| Purpose | File |
|:---|:---|
| Architecture reference | `.dev/ARCHITECTURE.md` |
| Port registry | `.dev/infra/registry.yml` |
| Current sprint | `.dev/roadmap/current-sprint.md` |
| Credentials | `.dev/context/credentials.md` |
| AI instructions | `CLAUDE.md` |

---

## MVP Roadmap (4 Weeks)

| Week | Focus | Status |
|:---|:---|:---:|
| Week 1 | UI Foundation + CSV Import | ✅ |
| Week 2 | Rule Engine + Workflow Logs | ✅ |
| Week 3 | Package Generation + UI Polish | ✅ |
| Week 4 | Auto Tests + CI/CD + Demo | 🚧 |

**Target Date:** December 20, 2025

---

## Access & Credentials

| Service | URL | Credentials |
|:---|:---|:---|
| SYNAPSE | http://localhost:4000 | admin@axoiq.com / admin123! |
| Grafana | http://localhost:3000 | admin / admin |
| pgAdmin | http://localhost:5050 | admin@axiom.local / admin |
| API Docs | http://localhost:4000/api/v1/docs | - |
| Prisma Studio | http://localhost:5555 | - |

**Full credentials:** [credentials.md](./credentials.md)

---

## AI Development Context

### Session Start Checklist

1. Read this file (`project-state.md`)
2. Check `.dev/roadmap/current-sprint.md`
3. Run `git status` for uncommitted changes
4. Use `/0-new-session` for full context load

### Key Commands

```bash
/0-new-session    # Start session (full context)
/0-next           # Continue next task
/0-progress       # View roadmap
/0-ship           # Git workflow
```

### Before Infrastructure Changes

**ALWAYS read `.dev/infra/registry.yml` first!**

---

## Known Issues

None currently.

---

## Next Steps

1. Complete auto tests setup
2. Setup CI/CD pipeline
3. Prepare demo dataset
4. Demo rehearsal (Dec 20)

---

*Updated: 2025-11-29*
