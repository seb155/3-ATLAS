# SYNAPSE - MBSE Platform

> **Model-Based Systems Engineering Platform for EPCM Automation**

## Overview

SYNAPSE is the core engineering application of the AXIOM platform, designed for Model-Based Systems Engineering (MBSE) in Engineering, Procurement, Construction, and Management (EPCM) environments.

## Key Features

### Asset Management
- 3-Tier Asset Model (Engineering, Catalog, Physical)
- Complete asset lifecycle tracking
- Hierarchical asset structures

### Breakdown Structures
- **FBS** - Functional Breakdown Structure
- **LBS** - Location Breakdown Structure
- **WBS** - Work Breakdown Structure
- **CBS** - Cost Breakdown Structure
- **PBS** - Product Breakdown Structure
- **OBS** - Organization Breakdown Structure

### Rule Engine
- Event-sourced rule processing
- Visual rule editor
- Impact analysis
- Automatic propagation

### Package Generation
- Excel exports
- PDF deliverables
- Custom templates

### Change Management
- Baseline creation
- Version history
- Impact analysis
- Audit trail

---

## Architecture

```
apps/synapse/
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
cd apps/synapse

# Start backend
cd backend
python -m uvicorn app.main:app --reload --port 8000

# Start frontend (new terminal)
cd frontend
npm run dev
```

**Access:** http://localhost:8080

---

## Related Documentation

- [Project Structure](../developer-guide/01-project-structure.md)
- [Rule Engine](../developer-guide/rule-engine-event-sourcing.md)
- [Workflow Engine](../developer-guide/workflow-engine.md)
- [Asset Lifecycle](../reference/asset-lifecycle.md)
- [Breakdown Structures](../reference/breakdown-structures-guide.md)
- [Impact Analysis](../reference/impact-analysis.md)
- [Package Deliverables](../reference/package-deliverables.md)

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python, FastAPI, SQLAlchemy |
| Frontend | React 19, TypeScript, TailwindCSS |
| Database | PostgreSQL (via FORGE) |
| Cache | Redis (via FORGE) |
| Search | MeiliSearch (via FORGE) |
