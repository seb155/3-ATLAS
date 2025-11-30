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
│  URL:           http://localhost:4000                            │
│  API:           http://localhost:4000/api/v1/docs                │
│  Credentials:   admin@aurumax.com / admin123!                    │
│                                                                  │
│  BACKEND:       cd apps/synapse/backend                          │
│                 uvicorn app.main:app --reload --port 8001        │
│                                                                  │
│  FRONTEND:      cd apps/synapse/frontend                         │
│                 npm run dev                                       │
│                                                                  │
│  TESTS:         pytest (backend)                                 │
│                 npm run test (frontend)                          │
│                                                                  │
│  DEMO DATA:     python -m app.scripts.seed_demo                  │
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
| Import | ✅ | CSV/Excel with validation |
| Export | ✅ | IN-P040, CA-P040 templates |
| Search | ✅ | MeiliSearch full-text |
| Real-time | ✅ | WebSocket logs |

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

- [ ] Setup auto tests
- [ ] CI/CD pipeline
- [ ] Demo dataset
- [ ] Plant 3D POC
- [ ] Demo rehearsal

---

*See `.dev/roadmap/` for detailed sprint info*
