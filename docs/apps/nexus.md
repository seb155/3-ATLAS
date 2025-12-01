# NEXUS - Knowledge Graph

> **Personal Knowledge Management & 3D Graph Visualization**

## Overview

NEXUS is a knowledge graph application for managing personal and organizational knowledge. It provides powerful 3D graph visualization ("FRED") and semantic search capabilities, with sync from TriliumNext.

## Key Features

### FRED - 3D Memory Graph
- **TriliumNext Sync** - Automatic import from personal notes
- **3D Visualization** - Interactive force-directed graph (Three.js)
- **Click-to-View** - Open notes as Markdown in side panel
- **Community Detection** - Auto-clustering related notes
- **Link Analysis** - Visual relationship mapping

### Knowledge Management
- Create and link knowledge nodes
- Rich text content with markdown
- Tags and categories
- Full-text search

### Graph Visualization
- Interactive 3D node-link diagrams
- Relationship mapping
- Clustering and grouping (Louvain algorithm)
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

### TriliumNext Integration
- ETAPI sync (real-time or scheduled)
- HTML to Markdown conversion
- Link extraction and graph building
- Bidirectional sync (planned)

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
| Backend | Python 3.11, FastAPI, SQLAlchemy |
| Frontend | React 19, TypeScript 5.9, Vite 7, TailwindCSS 4 |
| Database | PostgreSQL 15 (via FORGE) |
| Cache | Redis 7 (via FORGE) |
| Search | MeiliSearch (via FORGE) |
| Graph 3D | react-force-graph-3d, Three.js |
| Graph Analytics | NetworkX, python-louvain |
| Sync | trilium-py, html2text |
| State | Zustand |

---

## Development Status

| Phase | Status | Description |
|-------|--------|-------------|
| Phase 1 | ✅ Complete | UI Foundation (13 themes) |
| Phase 1.5 | ✅ Complete | Visual Polish |
| Phase 2 | 📋 Planned | Notes/Wiki + TriliumNext Sync |
| Phase 3 | 📋 Planned | Graph Analytics + FRED 3D |
| Phase 4 | 📋 Planned | Search + MeiliSearch |
| Phase 5 | 📋 Planned | Integration + Polish |

**Planning docs:**
- [NEXUS Development Plan](../../.dev/roadmap/nexus-development-plan.md)
- [Phase 2 Sprint](../../.dev/roadmap/nexus-phase-2-sprint.md)

---

## TriliumNext Sync Architecture

```
┌──────────────────┐     ETAPI      ┌──────────────────┐
│   TriliumNext    │ ────────────→  │  TriliumSync     │
│ notes.s-gagnon.com│               │    Service       │
└──────────────────┘                └────────┬─────────┘
                                             │
                    ┌────────────────────────┼────────────────────────┐
                    │                        ↓                        │
              ┌─────┴─────┐          ┌──────────────┐         ┌──────┴──────┐
              │   notes   │          │  note_links  │         │  sync_log   │
              │  (table)  │          │   (table)    │         │   (table)   │
              └─────┬─────┘          └──────────────┘         └─────────────┘
                    │
                    ↓
           ┌────────────────┐        ┌──────────────┐
           │  GraphService  │ ─────→ │    FRED      │
           │   (NetworkX)   │        │ (3D Graph)   │
           └────────────────┘        └──────┬───────┘
                                            │ click
                                            ↓
                                    ┌──────────────┐
                                    │ NoteViewer   │
                                    │ (Markdown)   │
                                    └──────────────┘
```
