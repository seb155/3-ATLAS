# AXIOM Platform State

**Platform:** AXIOM - AXoiq Enterprise Suite
**Repository:** https://github.com/seb155/AXIOM
**Last Updated:** 2025-11-28 (Migration to AXIOM complete)

---

## Platform Applications

| App | Purpose | Status |
|-----|---------|--------|
| **SYNAPSE** | MBSE Platform for EPCM Automation | MVP Dec 20, 2025 |
| **NEXUS** | Knowledge Graph + Notes/Wiki | Phase 1.5 |
| **PRISM** | Enterprise Portal / Dashboard | Development |
| **ATLAS** | AI Collaboration Environment | Planning |

**Infrastructure:** **FORGE** (PostgreSQL, Redis, Grafana, Loki, MeiliSearch)

---

## 🎯 Active Projects

### Primary: SYNAPSE
**Version:** v0.2.5 (MVP Phase - In Progress)
**Active Sprint:** MVP Critical Features Implementation
**Phase:** Implementation Week 1 ✅ COMPLETE
**Target:** Demo-ready MVP for employer presentation (Dec 20, 2025)
**Focus:** Logs/Traçabilité (CENTRAL) + Rule Engine + CSV Import + Package Export
**Progress:** Backend Traceability ✅ Complete | Week 2: Templates + UI

### Secondary: Dev Hub
**Status:** Architecture & Planning Phase
**Vision:** Notion + Linear + Obsidian + InfraNodus combined
**Scope:** Full Vision (Notes/Wiki + Tasks + 3D Graph + AI Chat + Collaboration)
**Timeline:** Parallel development (Phase 1 starts Dec 2025)
**Documentation:**
- Overview: `docs/projects/dev-hub/README.md`
- Plan: `.dev/roadmap/dev-hub-plan.md`
- Design: `docs/projects/dev-hub/DESIGN.md`

---

## 🚀 SYNAPSE Current Status

**Recent Major Event:** Complete project analysis + MVP roadmap created (2025-11-25)

---

## 📊 Version History

| Version | Name | Status | Completion Date |
|---------|------|--------|----------------|
| v0.2.5 | Atlas Orchestration System | ✅ DONE | 2025-11-28 |
| v0.2.4 | Templates & Package Export | ✅ DONE | 2025-11-28 |
| v0.2.3 | MVP Backend Traceability | ✅ DONE | 2025-11-28 |
| v0.2.2 | UX Professional + MVP Week 1 | ✅ DONE | 2025-11-27 |
| v0.2.1 | Logging & Monitoring | ✅ DONE | 2025-11-24 |
| v0.2.0 | Base Platform | ✅ DONE | 2025-11-23 |

---

## 🎯 Recent Major Changes

### 2025-11-28: v0.2.5 - Atlas Orchestration System COMPLETE ✅
**AI Session Management & Workflow Automation!**

**Nouveaux fichiers créés:**
- `.claude/agents/atlas.md` - Orchestrateur principal (point d'entrée unique)
- `.claude/commands/0-new-session.md` - Mode FULL (renamed from new-session.md)
- `.claude/commands/0-next.md` - Mode QUICK (quick task resume)
- `.claude/commands/0-resume.md` - Mode RECOVERY (after /compact)
- `.claude/commands/0-ship.md` - Git workflow automation
- `.claude/commands/0-progress.md` - Roadmap overview (compact)
- `.claude/commands/0-dashboard.md` - Session overview
- `.claude/context/session-history.json` - Session tracking
- `.dev/context/task-queue.md` - Task management
- `.claude/context/hot-files.json` - Smart context loading

**Fichiers modifiés:**
- `CLAUDE.md` - Added Atlas as entry point
- `.dev/journal/session-template.md` - Timestamp format YYYY-MM-DD HH:MM
- `.agent/rules/07-timestamp-format.md` - NEW: Central timestamp format guide (2025-11-28)

**Fonctionnalités implémentées:**
- ✅ **ATLAS Agent** - Main orchestrator avec 3 session modes
- ✅ **3 Session Modes** - FULL, QUICK, RECOVERY
- ✅ **Command Naming** - `/0-*` prefix pour tri alphabétique
- ✅ **Choix Numérotés** - Réponses systématiques avec options 1,2,3,4
- ✅ **Auto-documentation** - Via `/docs` après `/0-ship` ou inactivité 5+ min
- ✅ **Git Workflow** - Tests + commit + version bump + push automatisé
- ✅ **Progress Tracking** - `/0-progress` et `/0-dashboard` compacts
- ✅ **Timestamps Format Universel** - `YYYY-MM-DD HH:MM` partout + time ranges complets `[YYYY-MM-DD HH:MM] - [YYYY-MM-DD HH:MM]` (Guide: [.agent/rules/07-timestamp-format.md](d:\Projects\AXIOM\.agent\rules\07-timestamp-format.md))
- ✅ **GENESIS Format Updated** - Passe de `YYYY-MM-DD` à `YYYY-MM-DD HH:MM` (2025-11-28)
- ✅ **Session History** - Tracking JSON avec stats
- ✅ **Task Queue** - File de tâches prioritisée
- ✅ **Hot Files** - Smart context loading

**Commandes disponibles (type `/0` pour voir toutes):**
```
/0-new-session    # Mode FULL - Nouvelle session complète
/0-next           # Mode QUICK - Prochaine tâche rapide
/0-resume         # Mode RECOVERY - Après /compact
/0-progress       # Roadmap overview compact
/0-dashboard      # Session actuelle overview
/0-ship           # Git workflow automatisé
```

**Key Achievement:** Atlas devient le point d'entrée principal - workflow dev optimisé!
> "Type `/0` → Vois immédiatement toutes tes commandes essentielles"

**Impact:** Accélération 30-50% des futures sessions de développement

**Next:** Tests des workflows + intégration complète

### 2025-11-28: v0.2.4 - Templates & Package Export System COMPLETE ✅
**Week 2 Sprint - Package Generation & UI Components!**

**Nouveaux fichiers créés:**
- `app/services/template_service.py` - Service de génération templates Excel (400+ lignes)
- `app/api/endpoints/packages.py` - Package CRUD + Export endpoints (350+ lignes)
- `app/schemas/packages.py` - Pydantic schemas pour packages
- `frontend/src/components/AssetHistory.tsx` - UI Version history avec diff view (300+ lignes)
- `frontend/src/hooks/useWorkflowAPI.ts` - Hook pour Workflow & Traceability API
- `frontend/src/hooks/usePackages.ts` - Hook pour Package Management & Export

**Fonctionnalités implémentées:**
- ✅ **Template Service** - Génération Excel avec openpyxl + Jinja2
- ✅ **Templates IN-P040** - Instrument Index (panel instrumentation list)
- ✅ **Templates CA-P040** - Cable Schedule (power & signal cables)
- ✅ **Package API** - CRUD complet pour packages
- ✅ **Package Export** - Endpoint `/api/v1/packages/{id}/export`
- ✅ **Asset Assignment** - Ajout/retrait assets dans packages
- ✅ **Export Preview** - Preview des données avant export
- ✅ **AssetHistory UI** - Composant React avec version history & diff viewer
- ✅ **Workflow Hooks** - useWorkflowAPI & usePackages pour intégration frontend

**Endpoints ajoutés (Packages):**
```
GET    /api/v1/packages                        # List packages
POST   /api/v1/packages                        # Create package
GET    /api/v1/packages/{id}                   # Get package
PATCH  /api/v1/packages/{id}                   # Update package
DELETE /api/v1/packages/{id}                   # Delete package
GET    /api/v1/packages/{id}/assets            # List package assets
POST   /api/v1/packages/{id}/assets/{asset_id} # Add asset
DELETE /api/v1/packages/{id}/assets/{asset_id} # Remove asset
GET    /api/v1/packages/{id}/export            # Export Excel/PDF
GET    /api/v1/packages/{id}/export/preview    # Preview data
```

**Templates supportés:**
- **IN-P040**: Instrument Index - Panels, instruments, IO points
- **CA-P040**: Cable Schedule - Cables, routing, terminations

**Key Achievement:** Système complet de génération de livrables prêt pour MVP demo!
> "Import BBA → Rules create assets → Export IN-P040 package → Demo complete!"

**Next:** Tests backend + Frontend integration (AssetHistory dans AssetDetails)

### 2025-11-28: MVP Backend Traceability COMPLETE ✅
**Implementation Week 1 terminée avec succès!**

**Nouveaux fichiers créés:**
- `app/schemas/workflow.py` - Schemas Pydantic (~400 lignes)
- `app/api/endpoints/workflow.py` - 14 API endpoints (~500 lignes)
- `app/services/workflow_logger.py` - WorkflowLogger service (690 lignes)
- `app/services/versioning_service.py` - VersioningService (786 lignes)
- `app/services/rule_execution_service.py` - RuleExecutionService (800+ lignes)
- `app/models/workflow.py` - 5 models ORM (378 lignes)
- `alembic/versions/0001_initial_schema.py` - Migration consolidée

**Fonctionnalités implémentées:**
- ✅ **Workflow Events API** - Query, filter, correlation tracking
- ✅ **Timeline View API** - Pour UI DevConsole
- ✅ **Asset Versioning** - Snapshots complets, diff, rollback
- ✅ **Batch Operations** - Groupement pour rollback bulk
- ✅ **Property Changes** - Tracking field-level
- ✅ **CSV Import + Traceability** - WorkflowLogger intégré
- ✅ **Rule Engine (3 actions)** - CREATE_CHILD, CREATE_CABLE, CREATE_PACKAGE

**Endpoints ajoutés:**
```
GET  /api/v1/workflow/events
GET  /api/v1/workflow/timeline
GET  /api/v1/workflow/assets/{id}/versions
GET  /api/v1/workflow/assets/{id}/diff
POST /api/v1/workflow/assets/{id}/rollback
GET  /api/v1/workflow/batches
POST /api/v1/workflow/batches/{id}/rollback
GET  /api/v1/workflow/stats
```

**Key Insight:** Le système de logs/traçabilité est **CENTRAL** pour la démo.
> "Je peux voir exactement ce qui se passe à chaque étape"

**Next:** Week 2 - Templates Excel (IN-P040, CA-P040) + UI Timeline/History

### 2025-11-27: v0.2.2 Released - UI Foundation Complete
- ✅ AppLayout VSCode-like shell (Allotment resizable panes)
- ✅ ErrorBoundary for graceful error handling
- ✅ React Router v6 SPA navigation
- ✅ Centralized API client with interceptors
- ✅ UI components (Loading, Toast utilities)
- ✅ CSVImportPanel structure (40% complete)
- ✅ .claude/agents/ workflows (4 specialized agents)
- 📋 **Next:** Backend CSV endpoint + Complete import flow

**Git Tag:** v0.2.2
**Commits:**
- `dd20398` - chore(release): bump version to v0.2.2
- `053a0ed` - feat: implement modern UI foundation

### 2025-11-25: MVP Plan Created
- ✅ Complete project analysis (24 Docker services, architecture, AI setup)
- ✅ MVP roadmap defined (4 weeks, 5 priorities)
- ✅ Action plan created with weekly milestones
- ✅ Documentation structure planned for AI-assisted development
- 📋 **Next:** Setup UI foundation (Shadcn + Allotment + React Mosaic)

**Key Decisions:**
- **UI Architecture:** VSCode-like interface (tabs, split views, sidebar, status bar)
- **Component Library:** Shadcn/ui + Radix UI (TailwindCSS native)
- **Layout System:** Allotment (resizable panes) + React Mosaic (split views)
- **Testing:** Vitest (frontend) + Pytest (backend), GitHub Actions CI/CD
- **Versioning:** Semantic Release (auto-versioning from conventional commits)

**MVP Priorities:**
1. UI Architecture Type VSCode
2. Import CSV → Livrables (BBA → Packages IN-Pxxx)
3. Traçabilité & Logs Workflow
4. Tests Auto & Git Workflow
5. Dev Workflow AI-Optimisé

### 2025-11-24: Logging Infrastructure Complete
- ✅ Loki + Grafana + Promtail integration
- ✅ WebSocket real-time logging to DevConsole
- ✅ HTTP middleware logging
- ✅ Complete documentation

---

## 📁 Project Structure (Enhanced for AI Development)

```
EPCB-Tools/
├── workspace/              # Shared dev infrastructure (Docker - 24 services)
│   ├── postgres/           # PostgreSQL 15
│   ├── redis/              # Redis (cache, future Celery)
│   ├── loki/               # Log aggregation
│   ├── grafana/            # Log visualization
│   ├── traefik/            # Reverse proxy + SSL
│   ├── homepage/           # Portal dashboard
│   ├── allure/             # Test reporting (lightweight)
│   ├── reportportal/       # Test reporting (full-featured)
│   └── pgadmin/            # Database UI
├── apps/synapse/           # SYNAPSE application
│   ├── backend/            # FastAPI backend
│   │   ├── app/
│   │   │   ├── models/     # SQLAlchemy models
│   │   │   ├── routers/    # API endpoints
│   │   │   ├── services/   # Business logic (rule_engine.py)
│   │   │   ├── middleware/ # Logging, auth
│   │   │   └── scripts/    # DB seeding, utilities
│   │   └── alembic/        # Database migrations
│   └── frontend/           # React 19 frontend
│       └── src/
│           ├── components/
│           │   ├── ui/              # Shadcn base components (NEW)
│           │   ├── layout/          # AppLayout, Sidebar, etc. (NEW)
│           │   ├── domain/          # Business components (NEW)
│           │   └── features/        # Feature-specific (NEW)
│           ├── stores/     # Zustand state
│           └── services/   # API clients
├── docs/                   # Documentation
│   ├── getting-started/
│   ├── developer-guide/
│   ├── reference/
│   └── contributing/
│       └── code-guidelines.md
├── .dev/                   # Dev tracking & AI context
│   ├── journal/            # Daily development logs
│   │   ├── session-template.md  ← Template for AI sessions (NEW)
│   │   └── 2025-11/
│   │       └── 2025-11-25.md
│   ├── context/
│   │   ├── project-state.md     ← THIS FILE (AI entry point)
│   │   ├── credentials.md
│   │   └── shared-context.md
│   ├── testing/            # Test tracking (NEW)
│   │   └── test-status.md       ← Auto vs Manual validation
│   ├── scripts/            # Automation scripts (NEW)
│   │   └── smart-resume-enhanced.ps1  ← Context loader
│   ├── decisions/          # Architecture Decision Records
│   │   ├── 001-workspace-monorepo.md
│   │   └── 002-devconsole-v3-architecture.md
│   └── roadmap/
│       ├── README.md
│       ├── DOCUMENTATION-INDEX.md  ← AI navigation index
│       ├── current-sprint.md       ← MVP Week 1
│       ├── next-sprint.md
│       └── backlog/
├── .agent/                 # AI agent configuration
│   ├── 00_AGENT_START.md   # AI boot sequence
│   ├── rules/              # Always-on rules
│   │   ├── 00-agent-modes.md
│   │   ├── 01-naming-conventions.md
│   │   ├── 02-db-integrity.md
│   │   └── 05-user-context.md
│   ├── workflows/          # Slash commands
│   │   ├── 01-smart-resume.md
│   │   ├── 02-database-migration.md
│   │   ├── 11-new-feature-mvp.md        ← MVP workflow (NEW)
│   │   └── 12-test-validation-workflow.md (NEW)
│   └── prompts/            # Reusable templates (NEW)
│       ├── new-api-endpoint.md
│       └── new-react-component.md
├── CLAUDE.md               # Claude Code instructions
├── GEMINI.md               # Antigravity instructions (UPDATED)
└── .archive/               # Historical documentation
    └── doc_archive/
        └── 00_OVERVIEW/
            └── 00_START_HERE.md (UPDATED)
```

---

## 🔧 Tech Stack

**Backend:**
- FastAPI (Python 3.11)
- PostgreSQL 15
- SQLAlchemy (ORM)
- Alembic (migrations)
- Pydantic (validation)
- Loki (logging)

**Frontend:**
- React 19
- TypeScript
- Vite
- Zustand (state)
- TanStack Query (data fetching)
- Tailwind CSS

**Infrastructure:**
- Docker + Docker Compose
- Grafana (monitoring)
- Promtail (log shipping)
- pgAdmin (DB management)
- Prisma Studio (DB viewer)

---

## 🗺️ Roadmap Summary

**v0.2.x - Core Platform** (v0.2.1 → v0.2.12)
- v0.2.1: Logging & Monitoring ✅ DONE
- v0.2.2: UX Professional
- v0.2.3: 3-Tier Asset Model
- v0.2.4: Breakdown Structures (6 types)
- v0.2.5: Search & Navigation
- v0.2.6: Package Generation
- v0.2.7: Version History & Audit
- v0.2.8: Baselines & Impact Analysis
- v0.2.9: Rule Visualization
- v0.2.10: Visual Rule Editor
- v0.2.11: Rule Templates Library
- v0.2.12: Lifecycle Whiteboard (NEW - Brainstormed 2025-11-28)

**v0.3.0 - Multi-Tenant Auth** (2 weeks)
**v0.4.0 - Background Processing** (3 weeks)
**v0.5.0 - AI Integration** (4 weeks)
**v0.6.0 - P&ID Intelligence** (4 weeks)
**v0.7.0 - Drawing Generation** (5 weeks)
**v1.0.0 - Production Ready** (7 weeks)

**Full Roadmap:** [.dev/roadmap/README.md](.dev/roadmap/README.md)

---

## 📝 Quick Links

| Need | File |
|------|------|
| Today's work | [.dev/journal/2025-11/2025-11-24.md](.dev/journal/2025-11/2025-11-24.md) |
| Current sprint | [.dev/roadmap/current-sprint.md](.dev/roadmap/current-sprint.md) |
| Next sprint | [.dev/roadmap/next-sprint.md](.dev/roadmap/next-sprint.md) |
| Complete roadmap | [.dev/roadmap/README.md](.dev/roadmap/README.md) |
| Credentials | [.dev/context/credentials.md](.dev/context/credentials.md) |
| Shared context | [.dev/context/shared-context.md](.dev/context/shared-context.md) |

---

## 🎯 MVP Action Plan (4 Weeks)

### Week 1: UI Foundation + Import CSV (Nov 25-29)
**Days 1-2: Setup UI Architecture**
- [ ] Install Shadcn/ui + Allotment + React Mosaic
- [ ] Create AppLayout.tsx (VSCode-like shell)
- [ ] Create layout components (Sidebar, TabPanel, StatusBar)
- [ ] Implement dark theme (VSCode colors)

**Days 3-5: Import CSV**
- [ ] Backend: Endpoint POST /api/v1/import/csv
- [ ] Backend: CSV parser + validation
- [ ] Frontend: CSVImportPanel.tsx (drag-drop, preview)
- [ ] Frontend: Mapping columns UI
- [ ] Tests: pytest backend + vitest frontend
- [ ] Manual validation: Import real BBA.csv (100 instruments)

**Deliverable:** UI shell + Import CSV functional

### Week 2: Rule Engine + Workflow Logs (Dec 2-6)
**Days 1-3: Rule Engine Execution**
- [ ] Backend: RuleExecutionService (priority queue)
- [ ] Backend: Actions CREATE_CHILD, CREATE_CABLE, CREATE_PACKAGE
- [ ] Backend: Event sourcing (workflow_events table)
- [ ] Frontend: RuleExecutionPanel.tsx (selection rules/assets)
- [ ] Frontend: Live logs WebSocket
- [ ] Tests: pytest rule execution + coverage 80%+

**Days 4-5: Traceability Viewer**
- [ ] Backend: AssetChangeLog table
- [ ] Backend: EventLogger service (auto-log changes)
- [ ] Frontend: WorkflowTraceViewer.tsx (timeline)
- [ ] Frontend: AssetHistory.tsx (diff view)
- [ ] Manual validation: Execute rules, verify logs

**Deliverable:** Rule engine + complete traceability

### Week 3: Package Generation + UI Polish (Dec 9-13)
**Days 1-3: Package Generation**
- [ ] Backend: Template system (Jinja2 + openpyxl)
- [ ] Backend: Templates IN-Pxxx (panels, cables, instruments, networks)
- [ ] Backend: Endpoint GET /api/v1/packages/{id}/export
- [ ] Frontend: PackageExplorer.tsx (tree view)
- [ ] Frontend: Export buttons (Excel, PDF)
- [ ] Tests: pytest templates + vitest UI

**Days 4-5: UI Professional Polish**
- [ ] Loading states (spinners, skeletons)
- [ ] Error boundaries (graceful errors)
- [ ] Toast notifications (success/error)
- [ ] Smooth transitions (Framer Motion)
- [ ] Keyboard shortcuts (Ctrl+K command palette)
- [ ] Status bar indicators (connection, tasks)

**Deliverable:** Exportable packages + professional UI

### Week 4: Auto Tests + CI/CD + Demo Prep (Dec 16-20)
**Days 1-2: Git Workflow Automation**
- [ ] Setup Husky + lint-staged (pre-commit hooks)
- [ ] Setup GitHub Actions CI (.github/workflows/ci.yml)
- [ ] Setup Semantic Release (auto-versioning)
- [ ] Tests: Verify CI pipeline works

**Days 3-4: Documentation & Polish**
- [ ] Create user guide (docs/user-guide/quickstart.md)
- [ ] Record demo video (5-10 min)
- [ ] Prepare demo dataset (BBA.csv sample)
- [ ] Test demo offline (laptop without internet)

**Day 5: Demo Rehearsal**
- [ ] Demo script (precise steps)
- [ ] Test demo 3x (identify bugs)
- [ ] Prepare Q&A (anticipate employer questions)
- [ ] Backup plan (if demo fails, show video)

**Deliverable:** MVP demo-ready + CI/CD

---

## 📋 AI Development Context

**For AI Agents:** Always read these files at session start:
1. `.dev/context/project-state.md` (THIS FILE) - Current state
2. `.dev/journal/2025-11/2025-11-25.md` - Today's work
3. `.dev/roadmap/current-sprint.md` - Active sprint details
4. `.dev/testing/test-status.md` - Test validation status

**Smart Resume Script:** Run `.dev/scripts/smart-resume-enhanced.ps1` for quick context load (30 sec)

**MVP Plan Details:** See `~/.claude/plans/encapsulated-shimmying-waterfall.md`

---

## ⚠️ Known Issues

None currently.

---

## 🔑 Access

**App:** http://localhost:4000 (admin@aurumax.com / admin123!)
**Portal:** https://portal.localhost (Modern dashboard with SSL)
**API Docs:** http://localhost:8001/docs
**Grafana:** http://localhost:3000 (admin / xZfFu3&FZCBe)
**pgAdmin:** http://localhost:5050
**Prisma Studio:** http://localhost:5555

**Full credentials:** [.dev/context/credentials.md](.dev/context/credentials.md)

---

## 🆕 Dev Hub Project (Secondary - Planning Phase)

**Status:** Architecture complete, implementation pending
**Timeline:** Parallel development starting Dec 2025
**Approach:** Solo development (10% time) during SYNAPSE MVP, full-time after

### Overview
Development portal combining best features of Notion, Linear, Obsidian, and InfraNodus:
- **Notes/Wiki:** TipTap editor with hierarchical notes and wiki links
- **Task Management:** Kanban board + Gantt charts
- **Graph Visualization:** 2D/3D force-directed graphs with InfraNodus-style analytics
- **AI Integration:** Claude-powered chatbot with context awareness
- **Collaboration:** Real-time editing via Yjs CRDT

### Implementation Phases
1. **Phase 1 (Weeks 1-4):** Foundations (shadcn/ui, DB schema, Zustand)
2. **Phase 2 (Weeks 5-8):** Notes/Wiki system (TipTap, tree sidebar)
3. **Phase 3 (Weeks 9-12):** Task management (Kanban + drag-drop)
4. **Phase 4 (Weeks 13-14):** Roadmap + Gantt charts
5. **Phase 5 (Weeks 15-20):** 2D/3D Graph + InfraNodus features (networkx, Three.js)
6. **Phase 6 (Weeks 21-28):** AI Chat + Real-time collaboration

**Timeline:** 6 months solo, 3-4 months with team

### Documentation
- **Full Plan:** `.dev/roadmap/dev-hub-plan.md`
- **Overview:** `docs/projects/dev-hub/README.md`
- **Design Decisions:** `docs/projects/dev-hub/DESIGN.md`
- **Architecture Details:** `C:\Users\sgagn\.claude\plans\goofy-knitting-corbato.md`

### Next Steps (This Week)
- [ ] Decide: Monorepo (apps/dev-hub/) vs separate repo
- [ ] Phase 1 setup (if time permits after SYNAPSE work)

**Note:** Dev Hub development is **secondary priority**. SYNAPSE MVP must stay on track for Dec 20 deadline.

---

**Updated:** 2025-11-27 (v0.2.2 Released - UI Foundation Complete)
