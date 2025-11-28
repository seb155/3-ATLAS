# PRISM - Enterprise Portal

> **Unified Dashboard for Project Management & Analytics**

## Overview

PRISM is the enterprise portal component of AXIOM, providing a unified dashboard for project management, analytics, and cross-application integration.

## Key Features

### Dashboard
- Project overview widgets
- Key metrics and KPIs
- Activity feed
- Quick actions

### Project Management
- Project listing and filtering
- Status tracking
- Resource allocation
- Timeline views

### Analytics
- Data visualization
- Custom reports
- Export capabilities
- Trend analysis

### Integration Hub
- Links to SYNAPSE projects
- NEXUS knowledge access
- ATLAS AI insights
- Unified search

---

## Architecture

```
apps/prism/
├── backend/           # FastAPI Python backend
│   ├── app/
│   │   ├── api/       # REST endpoints
│   │   ├── core/      # Business logic
│   │   ├── models/    # SQLAlchemy models
│   │   └── services/  # Service layer
│   └── tests/
│
├── frontend/          # React TypeScript frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   └── services/
│   └── tests/
│
└── docker-compose.dev.yml
```

---

## Quick Start

```powershell
# From AXIOM root
cd apps/prism

# Start backend
cd backend
python -m uvicorn app.main:app --reload --port 8002

# Start frontend (new terminal)
cd frontend
npm run dev
```

**Access:** http://localhost:3002

---

## Status

**Current Status:** Development

PRISM is under active development. Core dashboard functionality is being built.

### Roadmap
- [ ] Project dashboard widgets
- [ ] Cross-app navigation
- [ ] Analytics module
- [ ] Report generation

---

## Related Documentation

- [Getting Started](../getting-started/01-installation.md)
- [Architecture Overview](../getting-started/03-architecture-overview.md)

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python, FastAPI, SQLAlchemy |
| Frontend | React 19, TypeScript, TailwindCSS |
| Database | PostgreSQL (via FORGE) |
| Cache | Redis (via FORGE) |
| Charts | Recharts, D3.js |
