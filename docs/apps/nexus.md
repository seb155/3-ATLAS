# NEXUS - Knowledge Graph

> **Personal Knowledge Management & Graph Visualization**

## Overview

NEXUS is a knowledge graph application for managing personal and organizational knowledge. It provides powerful graph visualization and semantic search capabilities.

## Key Features

### Knowledge Management
- Create and link knowledge nodes
- Rich text content with markdown
- Tags and categories
- Full-text search

### Graph Visualization
- Interactive node-link diagrams
- Relationship mapping
- Clustering and grouping
- Force-directed layouts

### Personal Portal
- Dashboard with recent items
- Quick capture
- Daily notes
- Bookmarks

### Search & Discovery
- MeiliSearch integration
- Semantic search
- Faceted filtering
- Related content suggestions

---

## Architecture

```
apps/nexus/
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
cd apps/nexus

# Start backend
cd backend
python -m uvicorn app.main:app --reload --port 8001

# Start frontend (new terminal)
cd frontend
npm run dev
```

**Access:** http://localhost:3001

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
| Search | MeiliSearch (via FORGE) |
| Graph | D3.js, Force Graph |
