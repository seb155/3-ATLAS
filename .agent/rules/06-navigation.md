---
trigger: model_decision
description: Navigation quick links to documentation, context, and credentials
---

# Navigation Quick Links

**Purpose:** Quick navigation to documentation, project state, and credentials.

**Timestamp Format:** Always use `YYYY-MM-DD HH:MM` (see [07-timestamp-format.md](d:\Projects\AXIOM\.agent\rules\07-timestamp-format.md))

---

## 📊 Project State & Tracking

**Current state:**
- **Version:** See `VERSION` file
- **Sprint:** `.dev/roadmap/current-sprint.md`
- **Project state:** `.dev/context/project-state.md` (MVP plan + status)
- **Today's work:** `.dev/journal/2025-11/YYYY-MM-DD.md`
- **Test tracking:** `.dev/testing/test-status.md`

**Dev tracking (`.dev/`):**
- `journal/` - Daily development logs
- `decisions/` - ADR (Architecture Decision Records)
- `roadmap/` - Sprint tracking + backlog
- `context/` - Shared context, credentials, project state
- `testing/` - Test status tracking

**Full index:** See `.dev/README.md`

---

## 📚 Documentation

**User documentation (`docs/`):**
- `getting-started/` - Quick start guide (5 minutes)
  - `01-installation.md`
  - `02-quick-tour.md`
  - `03-architecture-overview.md`
- `developer-guide/` - Deep dive
  - `01-project-structure.md`
  - `02-frontend-guide.md`
  - `03-backend-guide.md`
  - `04-database.md`
  - `05-testing.md`
  - `06-deployment.md`
- `reference/` - API docs, schemas, rules reference
- `contributing/` - Code guidelines, Git workflow

**Full documentation index:** See `docs/README.md`

---

## 🏗️ Architecture & Tech Stack

**Project structure:**
```
EPCB-Tools/
├── workspace/          # Shared dev infrastructure (24 Docker services)
├── apps/synapse/       # SYNAPSE application
│   ├── backend/        # FastAPI + SQLAlchemy
│   └── frontend/       # React 19 + TypeScript + Vite
├── docs/               # User documentation
└── .dev/               # Dev tracking & AI context
```

**Tech Stack:**
- **Backend:** FastAPI + SQLAlchemy + PostgreSQL
- **Frontend:** React 19 + TypeScript + TailwindCSS + Shadcn/ui
- **Infrastructure:** Docker Compose (workspace/apps monorepo)
- **Testing:** Pytest (backend) + Vitest (frontend)
- **Logging:** Loki + Grafana + Promtail

**Full details:**
- Architecture: `docs/getting-started/03-architecture-overview.md`
- Project structure: `docs/developer-guide/01-project-structure.md`
- Shared context: `.dev/context/shared-context.md`

---

## 🔑 Access & Credentials

**Single source:** `.dev/context/credentials.md`

**Quick reference:**
- **App:** http://localhost:4000
  - Login: `admin@aurumax.com` / `admin123!`
- **API Docs:** http://localhost:8001/docs (Swagger UI)
- **Portal:** https://portal.localhost (Traefik dashboard + Homepage)
- **Grafana:** http://localhost:3000 (Loki logs)
- **Prisma Studio:** http://localhost:5555 (Database viewer)
- **pgAdmin:** http://localhost:5050 (PostgreSQL admin)

**Full credentials:** See `.dev/context/credentials.md`

---

## 🗺️ Roadmap & Sprints

**Roadmap overview:**
- **Current version:** v0.2.2-dev (MVP Phase)
- **MVP target:** Dec 20, 2025 (4 weeks)
- **Target v1.0:** Aug 2026

**Sprint tracking:**
- **Overview:** `.dev/roadmap/README.md`
- **Current sprint:** `.dev/roadmap/current-sprint.md`
- **Next sprint:** `.dev/roadmap/next-sprint.md`
- **Backlog:** `.dev/roadmap/backlog/` (8 strategy files)

---

## 🗄️ Database

**Database info:**
- **Type:** PostgreSQL 15
- **Schema:** See `docs/developer-guide/04-database.md`
- **Main tables:** assets, cables, rules, projects, rule_executions
- **Migrations:** Alembic (see `/02-database-migration` workflow)

---

## 📦 Deployment

**Environments:**
- **DEV:** Workspace + apps (shared DB, 24 services)
- **PROD:** Standalone apps/synapse (future)

**Deployment guide:** See `docs/developer-guide/06-deployment.md`

---

## 🔍 Quick Navigation by Need

| Need | File |
|------|------|
| **Session start (Fast)** | `/00-start` workflow ⭐ (Gemini) |
| **Session start (Full)** | `/01-new-session` workflow (Legacy) |
| **Current MVP status** | `.dev/context/project-state.md` |
| **Today's work** | `.dev/journal/2025-11/YYYY-MM-DD.md` |
| **Test status** | `.dev/testing/test-status.md` |
| **Credentials** | `.dev/context/credentials.md` |
| **Roadmap** | `.dev/roadmap/README.md` |
| **Current sprint** | `.dev/roadmap/current-sprint.md` |
| **Architecture** | `docs/getting-started/03-architecture-overview.md` |
| **Code guidelines** | `docs/contributing/code-guidelines.md` |
| **Database schema** | `docs/developer-guide/04-database.md` |
| **Troubleshooting** | `GEMINI.md` (Common Issues section) |
| **AI setup** | `GEMINI.md` (for Antigravity) or `CLAUDE.md` (for Claude Code) |

---

## 🛠️ Common Issues (Quick Reference)

**Login 404 Error:**
1. Check PostgreSQL running: `docker ps --filter "name=postgres"`
2. Verify Vite proxy: `target: 'http://synapse-backend:8000'`
3. Restart services + hard refresh browser

**Backend DB Connection:**
1. Start PostgreSQL FIRST: `docker compose up -d forge-postgres`
2. Then restart backend: `docker restart synapse-backend`

**Full troubleshooting:** See `GEMINI.md` → Common Issues & Solutions

---

## 📖 Documentation Standards

**When to document:**
- New features → Update relevant `docs/developer-guide/`
- Decisions → Create ADR in `.dev/decisions/`
- Daily work → Log in `.dev/journal/YYYY-MM/YYYY-MM-DD.md`
- Releases → Create notes in `.dev/releases/`

**Style:** Concise, markdown, code examples

**Full guide:** See `docs/contributing/code-guidelines.md`

---

**Rule:** Reference docs/context files, don't duplicate architecture or credentials here.
