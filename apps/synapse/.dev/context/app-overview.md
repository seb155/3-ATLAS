# SYNAPSE - Application Overview

> **MBSE Platform for Engineering Automation**
>
> Status: MVP v0.2.5 | Target: December 20, 2025

---

## Quick Reference

```
┌─────────────────────────────────────────────────────────────────┐
│                    SYNAPSE QUICK REFERENCE                       │
├─────────────────────────────────────────────────────────────────┤
│  URL:           https://synapse.axoiq.com (or localhost:4000)   │
│  API:           https://api.axoiq.com/docs                       │
│  Credentials:   admin@aurumax.com / admin123!                    │
│                                                                  │
│  DOCKER:        cd apps/synapse                                  │
│                 docker compose -f docker-compose.dev.yml up -d   │
│                                                                  │
│  TESTS:         pytest (backend)                                 │
│                 npm run test (frontend)                          │
│                                                                  │
│  DEMO DATA:     Admin → Admin Tools → Seed Demo Data             │
│  CLEAR DATA:    Admin → Admin Tools → Clear All Data             │
│  ACTIVITY:      Admin → Activity Log                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## Purpose

SYNAPSE automates engineering workflows for EPCM projects:

1. **Import** - Load instrument/equipment data (CSV, Excel, Plant 3D)
2. **Rules** - Auto-generate related assets (motors, cables, packages)
3. **Export** - Generate professional Excel deliverables

---

## Key Features

| Feature | Status | Description |
|:--------|:------:|:------------|
| Asset Management | ✅ | CRUD, hierarchy, versioning |
| Rule Engine | ✅ | CREATE_CHILD, CREATE_CABLE, CREATE_PACKAGE |
| Audit Trail | ✅ | Event sourcing, diff, rollback |
| Import | ✅ | CSV/Excel with validation, case-insensitive headers |
| Export | ✅ | IN-P040, CA-P040 templates |
| Search | ✅ | MeiliSearch full-text |
| Real-time | ✅ | WebSocket logs |
| Admin Tools | ✅ | Seed data, execute rules, clear data |
| Activity Log | ✅ | Combined action_logs + workflow_events viewer |
| Project Mgmt | ✅ | Create, delete project, clear assets |

---

## Architecture

```
apps/synapse/
├── backend/           # FastAPI + Python 3.11
│   ├── app/
│   │   ├── api/       # REST endpoints
│   │   ├── services/  # Business logic
│   │   ├── models/    # SQLAlchemy ORM
│   │   └── schemas/   # Pydantic
│   └── tests/
│
├── frontend/          # React 19 + TypeScript
│   └── src/
│       ├── components/
│       ├── pages/
│       └── store/     # Zustand
│
└── .dev/              # This directory
```

---

## Current Sprint

**Week 4: Tests & Demo Preparation**

- [x] Setup auto tests (pre-commit hooks)
- [x] CI/CD pipeline (GitHub Actions)
- [x] Demo dataset (seed_demo.py via Admin Tools)
- [ ] Plant 3D POC
- [ ] Demo rehearsal

---

## Navigation Structure (Updated 2025-12-02)

```
📁 Project
   └── Overview (/dashboard)

📥 Data
   ├── Import (/modern-ingestion)
   └── Validation (/validation-results)

🔧 Engineering
   ├── Asset Explorer (/engineering)
   └── Locations (/locations)

⚡ Automation
   └── Rules Library (/rules)

📤 Outputs
   └── Cable Schedule (/cables)

🔒 Admin
   ├── Activity Log (/admin/activity)    ← NEW
   ├── Rule Executor (/rule-executor)
   ├── Admin Tools (/admin/tools)        ← NEW
   └── Metamodel (/metamodel)
```

---

## API Endpoints (Admin)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/admin/activity` | GET | Activity logs (combined) |
| `/api/v1/admin/stats` | GET | Project statistics |
| `/api/v1/admin/seed-demo` | POST | Seed demo data |
| `/api/v1/admin/execute-rules` | POST | Execute all rules |
| `/api/v1/admin/clear-data?confirm=true` | DELETE | Clear project data |
| `/api/v1/projects/projects/{id}` | DELETE | Delete project |
| `/api/v1/projects/projects/{id}/assets` | DELETE | Clear assets only |

---

*See `.dev/roadmap/` for detailed sprint info*
*See `.dev/context/session-2025-12-02.md` for today's changes*
