# AXIOM - Architecture Systeme Complete

> **Reference technique pour les agents AI et developpeurs**
>
> Derniere mise a jour: 2025-11-29 | Version: 0.2.5

---

## Table des matieres

1. [Vue d'ensemble](#1-vue-densemble)
2. [Applications Portfolio](#2-applications-portfolio)
3. [Architecture SYNAPSE](#3-architecture-synapse)
4. [FORGE Infrastructure](#4-forge-infrastructure)
5. [Systeme d'Agents AI](#5-systeme-dagents-ai)
6. [Allocation des Ports](#6-allocation-des-ports)
7. [Structure des Dossiers](#7-structure-des-dossiers)
8. [Stack Technologique](#8-stack-technologique)
9. [Roadmap](#9-roadmap)
10. [Fichiers Critiques](#10-fichiers-critiques)

---

## 1. Vue d'ensemble

### Diagramme Global

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AXIOM PLATFORM (Monorepo)                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │   SYNAPSE   │ │    NEXUS    │ │    PRISM    │ │    ATLAS    │           │
│  │  Port 4000  │ │  Port 5173  │ │  Port 6000  │ │  Port 7000  │           │
│  │ MBSE Engine │ │Knowledge Mgmt│ │  Dashboard  │ │AI Collab Env│           │
│  │  ✅ MVP     │ │  🔄 Dev     │ │  📋 Plan    │ │  📋 Plan    │           │
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

### Concept Cle

**AXIOM** = Monorepo unifie avec 4 applications partageant l'infrastructure **FORGE**

| Composant | Role |
|:---|:---|
| **Apps** | Applications metier independantes |
| **FORGE** | Infrastructure partagee (DB, cache, logs, search) |
| **forge-network** | Reseau Docker reliant toutes les apps |
| **.claude/** | Systeme d'agents AI pour le developpement |
| **.dev/** | Tracking developpement, contexte, roadmap |

---

## 2. Applications Portfolio

| App | Port | Description | Stack | Status |
|:---|:---:|:---|:---|:---:|
| **SYNAPSE** | 4000 | Plateforme MBSE - Automatisation EPCM | FastAPI + React 19 | MVP v0.2.5 |
| **NEXUS** | 5173 | Graphe de connaissances, notes, wiki | FastAPI + React | Phase 1.5 |
| **PRISM** | 6000 | Dashboard entreprise, metriques | TBD | Planning |
| **ATLAS** | 7000 | Environnement collaboration AI | TBD | Planning |

### SYNAPSE - Fonctionnalites MVP

| Module | Fonctionnalites | Status |
|:---|:---|:---:|
| **Asset Management** | CRUD, hierarchie parent/enfant, versioning, snapshots | ✅ |
| **Rule Engine** | CREATE_CHILD, CREATE_CABLE, CREATE_PACKAGE | ✅ |
| **Workflow/Audit** | Event sourcing, audit trail, diff calculation | ✅ |
| **Import/Export** | CSV/Excel import, validation, template export | ✅ |
| **Templates** | IN-P040 (Instrument Index), CA-P040 (Cable Schedule) | ✅ |
| **Search** | Full-text search via MeiliSearch | ✅ |
| **Packages** | WBS Package management, asset grouping | ✅ |
| **Real-time** | WebSocket logs, DevConsole | ✅ |
| **Auth** | JWT authentication, multi-tenant | ✅ |

---

## 3. Architecture SYNAPSE

### Vue Detaillee

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SYNAPSE APPLICATION                                 │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                         FRONTEND (React 19)                          │  │
│  │  ┌─────────────────────────────────────────────────────────────┐     │  │
│  │  │  UI Components (shadcn/ui + TailwindCSS)                    │     │  │
│  │  │  ├── Layout (VSCode-like shell, Allotment panels)           │     │  │
│  │  │  ├── Engineering Explorer (Asset tree, filters)             │     │  │
│  │  │  ├── Rule Editor (Definition, execution, logs)              │     │  │
│  │  │  ├── Import/Export (CSV, Excel templates)                   │     │  │
│  │  │  ├── Package Manager (WBS packages)                         │     │  │
│  │  │  └── DevConsole (Real-time WebSocket logs)                  │     │  │
│  │  └─────────────────────────────────────────────────────────────┘     │  │
│  │  State: Zustand │ Routing: React Router v6 │ Build: Vite            │  │
│  └─────────────────────────────────────────────────────────────────┬────┘  │
│                                                                    │       │
│                                              Vite Proxy /api/v1 ───┘       │
│                                                                    │       │
│  ┌─────────────────────────────────────────────────────────────────▼────┐  │
│  │                         BACKEND (FastAPI)                            │  │
│  │                                                                      │  │
│  │  ┌──────────────────────────────────────────────────────────────┐   │  │
│  │  │                      API ENDPOINTS                            │   │  │
│  │  │  /auth     /assets    /rules    /packages   /workflow        │   │  │
│  │  │  /search   /ingest    /export   /projects   /templates       │   │  │
│  │  └──────────────────────────────────────────────────────────────┘   │  │
│  │                               │                                      │  │
│  │  ┌────────────────────────────▼─────────────────────────────────┐   │  │
│  │  │                      SERVICES (18)                            │   │  │
│  │  │  ┌─────────────────┐ ┌─────────────────┐ ┌────────────────┐  │   │  │
│  │  │  │  Rule Engine    │ │ Workflow Logger │ │ Template Svc   │  │   │  │
│  │  │  │  (3 actions:    │ │ (Event sourcing │ │ (IN-P040,      │  │   │  │
│  │  │  │  CREATE_CHILD,  │ │  Audit trail,   │ │  CA-P040       │  │   │  │
│  │  │  │  CREATE_CABLE,  │ │  Versioning)    │ │  Excel export) │  │   │  │
│  │  │  │  CREATE_PKG)    │ │                 │ │                │  │   │  │
│  │  │  └─────────────────┘ └─────────────────┘ └────────────────┘  │   │  │
│  │  │  ┌─────────────────┐ ┌─────────────────┐ ┌────────────────┐  │   │  │
│  │  │  │ Ingestion Svc   │ │ MeiliSearch Svc │ │ AI Provider    │  │   │  │
│  │  │  │ (CSV/Excel      │ │ (Full-text      │ │ (Claude API)   │  │   │  │
│  │  │  │  import)        │ │  search)        │ │                │  │   │  │
│  │  │  └─────────────────┘ └─────────────────┘ └────────────────┘  │   │  │
│  │  └──────────────────────────────────────────────────────────────┘   │  │
│  │                               │                                      │  │
│  │  ┌────────────────────────────▼─────────────────────────────────┐   │  │
│  │  │                      MODELS (SQLAlchemy ORM)                  │   │  │
│  │  │  Asset │ Project │ Rule │ Package │ WorkflowEvent │ Cable    │   │  │
│  │  │  User  │ Client  │ Metamodel │ ActionLog │ AuditTrail        │   │  │
│  │  └──────────────────────────────────────────────────────────────┘   │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Backend Structure

```
apps/synapse/backend/app/
├── main.py                        # FastAPI app + exception handlers
├── api/
│   └── endpoints/                 # REST API endpoints
│       ├── assets.py              # Asset CRUD
│       ├── auth.py                # Authentication
│       ├── packages.py            # Package management
│       ├── rules.py               # Rule definitions
│       ├── workflow.py            # Workflow & traceability
│       ├── search.py              # Full-text search
│       ├── import_export.py       # CSV/Excel import-export
│       └── [10 total endpoints]
├── services/                      # Business logic (18 services)
│   ├── rule_execution_service.py  # Rule engine execution
│   ├── workflow_logger.py         # Event sourcing & audit trails
│   ├── versioning_service.py      # Asset versioning & snapshots
│   ├── rule_engine.py             # Rule evaluation
│   ├── template_service.py        # Excel template generation
│   ├── meilisearch_service.py     # Full-text search integration
│   ├── ai_provider.py             # Claude/AI integration
│   ├── cable_sizing.py            # Electrical calculations
│   ├── ingestion_service.py       # CSV parsing
│   └── action_logger.py           # Action audit log
├── models/                        # SQLAlchemy ORM
│   ├── models.py                  # Core entities
│   ├── packages.py                # Package & WBS structures
│   ├── rules.py                   # Rule definitions
│   ├── workflow.py                # Workflow events
│   └── [9 total models]
├── schemas/                       # Pydantic schemas
├── core/
│   ├── database.py                # DB connection
│   ├── config.py                  # Settings
│   ├── auth.py                    # JWT
│   └── exceptions.py              # Custom exceptions
└── scripts/
    └── seed_demo.py               # Demo data generator
```

### Frontend Structure

```
apps/synapse/frontend/src/
├── App.tsx                        # Main app
├── components/
│   ├── ui/                        # shadcn/ui components
│   ├── layout/                    # AppLayout, Sidebar
│   ├── explorer/                  # Engineering explorer
│   ├── rules/                     # Rule editor
│   ├── projects/                  # Project management
│   └── DevConsole/                # Real-time logs
├── pages/                         # Route pages
├── hooks/                         # Custom hooks
├── services/                      # API clients
├── store/                         # Zustand state
├── types/                         # TypeScript types
└── utils/                         # Utilities
```

---

## 4. FORGE Infrastructure

### Services Partages

| Service | Container | Port | Image | Purpose |
|:---|:---|:---:|:---|:---|
| **PostgreSQL** | `forge-postgres` | 5433 | postgres:15-alpine | Base de donnees |
| **Redis** | `forge-redis` | 6379 | redis:7-alpine | Cache & sessions |
| **Loki** | `forge-loki` | 3100 | grafana/loki:3.0.0 | Aggregation logs |
| **Promtail** | `forge-promtail` | - | grafana/promtail:2.9.0 | Collecteur logs |
| **Grafana** | `forge-grafana` | 3000 | grafana/grafana:10.0.0 | Dashboards |
| **MeiliSearch** | `forge-meilisearch` | 7700 | getmeili/meilisearch:v1.5 | Full-text search |
| **pgAdmin** | `forge-pgadmin` | 5050 | dpage/pgadmin4:latest | PostgreSQL GUI |
| **Prisma Studio** | `forge-prisma` | 5555 | prisma/studio:latest | DB browser |
| **Traefik** | `forge-traefik` | 80, 443, 8888 | traefik:v3.6.2 | Reverse proxy |
| **Wiki** | `forge-wiki` | 3080 | nginx:alpine | Documentation |

### Ordre de Demarrage

```
Tier 1 (Base):      PostgreSQL, Redis
Tier 2 (Logs):      Loki, MeiliSearch
Tier 3 (Monitor):   Promtail, Grafana
Tier 4 (Proxy):     Traefik
Tier 5 (Apps):      SYNAPSE backend, NEXUS backend
Tier 6 (Frontend):  SYNAPSE frontend, NEXUS frontend
```

### Reseau Docker

```
┌─────────────────────────────────────────────────────────────────┐
│                        forge-network                             │
│                                                                 │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐               │
│  │   SYNAPSE   │ │    NEXUS    │ │   PRISM     │               │
│  │   backend   │ │   backend   │ │  (future)   │               │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘               │
│         │               │               │                       │
│         └───────────────┴───────────────┘                       │
│                         │                                       │
│  ┌──────────────────────┴──────────────────────────┐           │
│  │ forge-postgres │ forge-redis │ forge-meilisearch │           │
│  └──────────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. Systeme d'Agents AI

### Architecture des Agents

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AI AGENTS SYSTEM                                  │
│                                                                             │
│  ┌─────────────────────── ORCHESTRATEURS (Opus) ─────────────────────────┐ │
│  │                                                                        │ │
│  │  ┌─────────┐   ┌─────────┐   ┌──────────────┐   ┌─────────┐          │ │
│  │  │  ATLAS  │   │ GENESIS │   │SYSTEM-ARCHI- │   │BRAINSTORM│          │ │
│  │  │ (Main)  │   │ (Meta)  │   │    TECT      │   │(Creative)│          │ │
│  │  │         │   │         │   │              │   │          │          │ │
│  │  │ Session │   │ AI      │   │ Governance   │   │ Design   │          │ │
│  │  │ Routing │   │ Evolut° │   │ Bypass       │   │ Thinking │          │ │
│  │  └────┬────┘   └─────────┘   └──────────────┘   └──────────┘          │ │
│  └───────┼───────────────────────────────────────────────────────────────┘ │
│          │                                                                  │
│          ▼                                                                  │
│  ┌───────────────────── AGENTS SPECIALISES ────────────────────────────┐   │
│  │                                                                      │   │
│  │  BUILDERS           VALIDATORS        TRACKERS         PLANNERS     │   │
│  │  ┌─────────────┐   ┌────────────┐   ┌────────────┐   ┌───────────┐  │   │
│  │  │ Backend     │   │ QA Tester  │   │ Dev Tracker│   │ Debugger  │  │   │
│  │  │ Frontend    │   │ Issue      │   │ Git Manager│   │ Planner   │  │   │
│  │  │ DevOps      │   │ Reporter   │   │            │   │ UX Design │  │   │
│  │  │ Architect   │   │            │   │            │   │           │  │   │
│  │  │ Integration │   │            │   │            │   │           │  │   │
│  │  └─────────────┘   └────────────┘   └────────────┘   └───────────┘  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  COMMANDS:  /0-new-session  /0-next  /0-resume  /0-progress  /0-ship       │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Agents par Categorie

| Categorie | Agent | Modele | Fichier | Purpose |
|:---|:---|:---:|:---|:---|
| **Orchestrators** | ATLAS | Opus | `agents/atlas.md` | Main orchestrator |
| | GENESIS | Opus | `agents/orchestrators/genesis.md` | AI evolution |
| | BRAINSTORM | Opus | `agents/orchestrators/brainstorm.md` | Creative sessions |
| | SYSTEM-ARCHITECT | Opus | `agents/orchestrators/system-architect.md` | Governance |
| **Builders** | Backend | Sonnet | `agents/builders/backend-builder.md` | Backend code |
| | Frontend | Sonnet | `agents/builders/frontend-builder.md` | Frontend code |
| | DevOps | Sonnet | `agents/builders/devops-builder.md` | Infrastructure |
| | Architect | Opus | `agents/builders-opus/architect-builder.md` | Architecture |
| | Integration | Opus | `agents/builders-opus/integration-builder.md` | Integration |
| **Validators** | QA-Tester | Haiku | `agents/validators/qa-tester.md` | Tests |
| | Issue-Reporter | Haiku | `agents/validators/issue-reporter.md` | Issues |
| **Trackers** | Dev-Tracker | Haiku | `agents/trackers/dev-tracker.md` | Progress |
| | Git-Manager | Haiku | `agents/trackers/git-manager.md` | Git ops |
| **Planners** | Debugger | Sonnet | `agents/planners/debugger.md` | Debug |
| | Planner | Sonnet | `agents/planners/planner.md` | Planning |
| | UX-Designer | Sonnet | `agents/planners/ux-designer.md` | UI/UX |
| **Special** | DevOps-Manager | Opus | `agents/devops-manager.md` | Infrastructure |

### Commandes Session

| Commande | Mode | Description |
|:---|:---|:---|
| `/0-new-session` | FULL | Premiere session - charge tout le contexte |
| `/0-next` | QUICK | Continue tache suivante (minimal) |
| `/0-resume` | RECOVERY | Apres /compact |
| `/0-progress` | - | Vue roadmap compacte |
| `/0-dashboard` | - | Status session courante |
| `/0-ship` | - | Git workflow (test + commit + push) |

---

## 6. Allocation des Ports

### Strategie

Chaque application a une plage de 1000 ports dediee:

```
Port Range Allocation
─────────────────────────────────────────────────────────────
│ 3000-3999 │ FORGE        │ ████████░░ │ 9 alloues    │
│ 4000-4999 │ SYNAPSE      │ ██░░░░░░░░ │ 2 alloues    │
│ 5000-5999 │ NEXUS        │ ██░░░░░░░░ │ 2 alloues    │
│ 6000-6999 │ PRISM        │ ░░░░░░░░░░ │ 0 alloues    │
│ 7000-7999 │ ATLAS        │ ░░░░░░░░░░ │ 0 alloues    │
─────────────────────────────────────────────────────────────
```

### Detail par Application

**FORGE (3000-3999)**
| Port | Service |
|:---:|:---|
| 3000 | Grafana |
| 3080 | Wiki (Docsify) |
| 3100 | Loki |
| 5050 | pgAdmin |
| 5433 | PostgreSQL |
| 5555 | Prisma Studio |
| 6379 | Redis |
| 7700 | MeiliSearch |
| 80/443 | Traefik |

**SYNAPSE (4000-4999)**
| Port | Service |
|:---:|:---|
| 4000 | Frontend (React + Vite) |
| 8001 | Backend (FastAPI) - grandfathered |

**NEXUS (5000-5999)**
| Port | Service |
|:---:|:---|
| 5173 | Frontend |
| 8000 | Backend |

### Source de Verite

`.dev/infra/registry.yml` - Toujours consulter avant toute allocation de port!

---

## 7. Structure des Dossiers

```
AXIOM/
├── apps/
│   ├── synapse/                 # App MBSE principale
│   │   ├── backend/
│   │   │   ├── app/             # Code source FastAPI
│   │   │   ├── tests/           # Tests pytest
│   │   │   ├── alembic/         # Migrations DB
│   │   │   └── requirements.txt
│   │   ├── frontend/
│   │   │   ├── src/             # Code source React
│   │   │   ├── public/
│   │   │   └── package.json
│   │   └── docker-compose.dev.yml
│   ├── nexus/                   # Knowledge Graph
│   ├── prism/                   # Dashboard
│   └── atlas/                   # AI Collab
│
├── forge/
│   ├── docker-compose.yml       # Infrastructure partagee
│   ├── config/                  # Configurations services
│   └── init/                    # Scripts initialisation
│
├── .claude/
│   ├── agents/                  # Definitions des agents
│   │   ├── atlas.md             # Orchestrateur principal
│   │   ├── orchestrators/       # Agents Opus
│   │   ├── builders/            # Agents construction
│   │   ├── validators/          # Agents validation
│   │   ├── trackers/            # Agents suivi
│   │   └── planners/            # Agents planification
│   ├── commands/                # Slash commands
│   │   ├── 0-new-session.md
│   │   ├── 0-next.md
│   │   └── [autres commandes]
│   ├── skills/                  # Skills reutilisables
│   └── context/                 # Contexte session
│
├── .dev/
│   ├── ARCHITECTURE.md          # CE FICHIER
│   ├── README.md                # Index dev tracking
│   ├── context/
│   │   ├── project-state.md     # Etat MVP courant
│   │   ├── credentials.md       # Identifiants
│   │   └── task-queue.md        # File taches
│   ├── infra/
│   │   ├── registry.yml         # REGISTRE PORTS (CRITIQUE!)
│   │   ├── infrastructure.md    # Doc infrastructure
│   │   └── CHANGELOG.md         # Historique changes
│   ├── journal/
│   │   └── 2025-11/             # Logs quotidiens
│   ├── roadmap/
│   │   ├── current-sprint.md    # Sprint actuel
│   │   └── backlog/             # Backlog items
│   ├── decisions/               # ADR (Architecture Decision Records)
│   └── testing/
│       └── test-status.md       # Status tests
│
├── docs/                        # Documentation publique
│   ├── getting-started/         # Guides demarrage
│   ├── developer-guide/         # Guide developpeur
│   ├── reference/               # Documentation reference
│   ├── workflows/               # Workflows utilisateur
│   └── infrastructure/          # Guide infrastructure
│
├── CLAUDE.md                    # Instructions AI principales
└── README.md                    # README GitHub
```

---

## 8. Stack Technologique

### Frontend

| Technologie | Version | Usage |
|:---|:---|:---|
| React | 19 | UI framework |
| TypeScript | 5.x | Type safety |
| Vite | 7.2 | Build tool |
| Zustand | 5.x | State management |
| TailwindCSS | 4.x | Styling |
| shadcn/ui | Latest | Component library |
| React Router | 6.x | Navigation |
| Allotment | Latest | Resizable panes |

### Backend

| Technologie | Version | Usage |
|:---|:---|:---|
| Python | 3.11+ | Language |
| FastAPI | 0.121+ | Web framework |
| SQLAlchemy | 2.0+ | ORM |
| Pydantic | 2.x | Validation |
| Alembic | Latest | Migrations |
| pytest | Latest | Testing |
| ruff | Latest | Linting |

### Infrastructure

| Technologie | Version | Usage |
|:---|:---|:---|
| Docker | Latest | Containerisation |
| Docker Compose | Latest | Orchestration |
| PostgreSQL | 15 | Database |
| Redis | 7 | Cache |
| MeiliSearch | 1.5 | Search |
| Loki | 3.0 | Logs |
| Grafana | 10.0 | Monitoring |
| Traefik | 3.6 | Reverse proxy |

### AI/Agents

| Technologie | Modele | Usage |
|:---|:---|:---|
| Claude | Opus | Orchestration, architecture |
| Claude | Sonnet | Implementation, planning |
| Claude | Haiku | Validation, tracking |

---

## 9. Roadmap

### SYNAPSE MVP (Q4 2025)

**Objectif:** Demo-ready pour 20 decembre 2025

| Semaine | Focus | Status |
|:---|:---|:---:|
| Week 1 | UI Foundation + CSV Import | ✅ |
| Week 2 | Rule Engine + Workflow Logs | ✅ |
| Week 3 | Package Generation + UI Polish | ✅ |
| Week 4 | Auto Tests + CI/CD + Demo | 🚧 |

### Features Completees

- [x] VSCode-like UI architecture (Allotment, React Mosaic)
- [x] CSV/Excel import with validation
- [x] Rule engine with 3 action types
- [x] Complete audit trail & versioning
- [x] Excel template export (IN-P040, CA-P040)
- [x] Package management system
- [x] Real-time WebSocket logging
- [x] Full-text search integration

### Next (Q1 2026)

- [ ] NEXUS Phase 2 - Backend integration
- [ ] PRISM initial release
- [ ] Multi-tenant improvements
- [ ] CI/CD pipeline complete

### Future

- [ ] ATLAS AI Collaboration app
- [ ] Mobile companion
- [ ] Advanced AI integrations

---

## 10. Fichiers Critiques

### A Consulter en Priorite

| Fichier | Taille | Purpose | Quand |
|:---|:---:|:---|:---|
| `.dev/infra/registry.yml` | 17 KB | Registre ports/services | AVANT toute operation infra |
| `.dev/context/project-state.md` | 22 KB | Etat MVP courant | Debut de session |
| `CLAUDE.md` | - | Instructions AI | Toujours |
| `.dev/roadmap/current-sprint.md` | - | Sprint actuel | Planning |

### Fichiers de Configuration

| Fichier | Purpose |
|:---|:---|
| `forge/docker-compose.yml` | Infrastructure FORGE |
| `apps/synapse/docker-compose.dev.yml` | Dev SYNAPSE |
| `apps/synapse/backend/alembic.ini` | Migrations DB |
| `apps/synapse/frontend/vite.config.ts` | Build frontend |

### Documentation Reference

| Fichier | Purpose |
|:---|:---|
| `.dev/infra/infrastructure.md` | Guide infrastructure complet |
| `docs/developer-guide/rule-engine-event-sourcing.md` | Rule engine deep dive |
| `docs/developer-guide/ai-agents-overview.md` | Systeme agents |

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────────┐
│                    AXIOM QUICK REFERENCE                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
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
│    pgAdmin:    admin@axiom.local / admin                        │
│                                                                 │
│  COMMANDS:                                                      │
│    /0-new-session   Start new session (full context)            │
│    /0-next          Continue next task                          │
│    /0-ship          Git workflow (test + commit + push)         │
│                                                                 │
│  DEMO DATA:    python -m app.scripts.seed_demo                  │
│                                                                 │
│  KEY FILES:                                                     │
│    .dev/infra/registry.yml     Port registry (READ FIRST!)     │
│    .dev/context/project-state.md   Current MVP status           │
│    CLAUDE.md                   AI instructions                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

*Document genere pour reference AI et developpeurs - Maintenir a jour!*
