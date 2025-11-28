# EPCB-Tools Project State

**Primary Project:** SYNAPSE - MBSE Platform for EPCM Automation
**Secondary Project:** Dev Hub - Development Portal (Planning Phase)
**Last Updated:** 2025-11-28 (Whiteboard Session + Lifecycle Whiteboard complete)

---

## 🎯 Active Projects

### Primary: SYNAPSE
**Version:** v0.2.2 (MVP Phase - In Progress)
**Active Sprint:** MVP Critical Features Design & Implementation
**Phase:** Design Complete → Implementation Starting
**Target:** Demo-ready MVP for employer presentation (Dec 20, 2025)
**Focus:** Logs/Traçabilité (CENTRAL) + Rule Engine + CSV Import + Package Export
**Progress:** Design ✅ Complete | Implementation 🔄 Starting Dec 2

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
| v0.2.2 | UX Professional + MVP Week 1 | 🔄 IN PROGRESS | 2025-11-29 (Target) |
| v0.2.1 | Logging & Monitoring | ✅ DONE | 2025-11-24 |
| v0.2.0 | Base Platform | ✅ DONE | 2025-11-23 |

---

## 🎯 Recent Major Changes

### 2025-11-28: Whiteboard Session - MVP Design Complete
- ✅ **Architecture Review:** Comprehensive security & code quality analysis
- ✅ **Système de Logs Design:** `workflow_events`, Timeline view, Asset History
- ✅ **Rule Engine Design:** 3 actions MVP (CREATE_CHILD, CREATE_CABLE, CREATE_PACKAGE)
- ✅ **CSV Import Design:** 5-stage pipeline avec logging complet
- ✅ **Package Export Design:** Jinja2 + openpyxl templates
- ✅ **Security Fixes:** Secrets, CORS, project validation, indexes
- 📋 **Next:** Implementation starting Dec 2

**Key Documents:**
- `.dev/design/2025-11-28-whiteboard-session.md` - Full design specs
- `.dev/analysis/2025-11-28-architecture-review.md` - Security & quality fixes
- `docs/DEPLOYMENT.md` - Production deployment guide

**Key Insight:** Le système de logs/traçabilité est **CENTRAL** pour la démo.
> "Je peux voir exactement ce qui se passe à chaque étape"

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
