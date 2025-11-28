# Search & Navigation

**Version:** v0.2.2 (MeiliSearch) → v0.2.5 (Advanced Filters)
**Status:** MEILISEARCH IMPLEMENTED
**Goal:** Fast, typo-tolerant search with advanced filtering for 10K+ assets

---

## Implementation Status

### ✅ Phase 1: Basic Search (v0.2.2) - DONE
- [x] Command Palette (Ctrl+K / Cmd+K)
- [x] Global search bar in title bar
- [x] Fuzzy matching with `thefuzz` (fallback)
- [x] Search across assets, rules, cables, locations
- [x] Navigation shortcuts
- [x] Quick actions
- [x] Recent searches (localStorage)

### ✅ Phase 1.5: MeiliSearch Integration (v0.2.2) - DONE
- [x] MeiliSearch v1.11 in Docker (MIT License - 100% Free)
- [x] Multi-index search (assets, rules, cables, locations)
- [x] Typo-tolerant full-text search (~10ms for 10K+ docs)
- [x] Automatic fallback to thefuzz when MeiliSearch unavailable
- [x] Re-indexing API endpoints
- [x] Index statistics endpoint
- [x] Project-based filtering

### 🔄 Phase 2: Advanced Filtering (v0.2.5) - PLANNED
- [ ] Filter chips with lock/unlock
- [ ] Project filter (default: active project)
- [ ] Discipline quick filters (Electrical, Mechanical, Process)
- [ ] Property-based suggestions
- [ ] Filter persistence (user preferences)
- [ ] Saved searches
- [ ] Faceted search with counts (MeiliSearch native)

---

## MeiliSearch Implementation Details

### Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         SYNAPSE Frontend                            │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Command Palette (Ctrl+K)  │  Search Bar (Title Bar)         │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                               │                                     │
│                               ▼                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              searchService.ts (API Client)                   │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         SYNAPSE Backend                             │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  /api/v1/search/ - Global Search Endpoint                    │  │
│  │  ├── GET /           - Search (MeiliSearch primary)          │  │
│  │  ├── GET /suggestions - Autocomplete                         │  │
│  │  ├── GET /status     - Index health & stats                  │  │
│  │  ├── POST /reindex   - Full reindex (background)             │  │
│  │  └── POST /reindex/{type} - Reindex specific entity          │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                               │                                     │
│            ┌──────────────────┴──────────────────┐                  │
│            ▼                                     ▼                  │
│  ┌─────────────────────┐              ┌─────────────────────┐      │
│  │ MeiliSearch Service │              │  thefuzz Fallback   │      │
│  │   (Primary)         │              │  (When unavailable) │      │
│  └─────────────────────┘              └─────────────────────┘      │
└─────────────────────────────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    MeiliSearch Container                            │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  forge-meilisearch:7700                                  │  │
│  │  ├── synapse_assets   (tag, description, system, area)       │  │
│  │  ├── synapse_rules    (name, description, trigger_type)      │  │
│  │  ├── synapse_cables   (tag, from_location, to_location)      │  │
│  │  └── synapse_locations (name, code)                          │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### Docker Setup (Already Configured)

```yaml
# workspace/docker-compose.yml
services:
  meilisearch:
    image: getmeili/meilisearch:v1.11
    container_name: forge-meilisearch
    environment:
      MEILI_ENV: development
      MEILI_MASTER_KEY: ${MEILI_MASTER_KEY:-synapse_dev_key_change_in_prod}
      MEILI_NO_ANALYTICS: "true"
    volumes:
      - meilisearch-data:/meili_data
    ports:
      - "7700:7700"
    networks:
      - forge-network
    healthcheck:
      test: ["CMD", "wget", "--no-verbose", "--spider", "http://localhost:7700/health"]
```

### Backend Service

**File:** `backend/app/services/meilisearch_service.py`

```python
# Key functions
get_meilisearch_service()  # Singleton instance
service.is_available()      # Health check
service.search(query, indexes, project_id, limit)  # Multi-index search
service.index_assets_batch(docs)  # Batch indexing
service.initialize_indexes()  # Create indexes with settings
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/search/` | GET | Global search (MeiliSearch or fallback) |
| `/api/v1/search/suggestions` | GET | Autocomplete suggestions |
| `/api/v1/search/status` | GET | Index health and statistics |
| `/api/v1/search/reindex` | POST | Full reindex (background task) |
| `/api/v1/search/reindex/{type}` | POST | Reindex specific entity type |

### Index Configuration

Each index has optimized settings:

```python
# Assets Index
{
    "searchableAttributes": ["tag", "description", "system", "area", "io_type", "discipline"],
    "filterableAttributes": ["project_id", "discipline", "system", "area", "io_type", "type"],
    "sortableAttributes": ["tag", "created_at"],
    "typoTolerance": {"enabled": True, "minWordSizeForTypos": {"oneTypo": 3, "twoTypos": 6}}
}
```

### Performance Characteristics

| Metric | MeiliSearch | thefuzz (Fallback) |
|--------|-------------|-------------------|
| Search 3K docs | ~10ms | ~100-150ms |
| Search 10K docs | ~15ms | ~500ms |
| Typo tolerance | Built-in | Manual |
| Faceted filters | Native | Not available |
| Memory usage | ~200MB | Minimal |

---

## Phase 2: Advanced Filtering Specification

### Overview

Enhance the existing Command Palette with intelligent filtering:

```
┌─────────────────────────────────────────────────────────────────────────┐
│  🔍 Search...                                                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Filtres actifs:                                                        │
│  ┌─────────────────┐ ┌─────────────────┐ ┌───────────────────────────┐ │
│  │ 🔒 Sigma Mine   │ │ 🔒 ⚡ Électrique │ │ Area: 310            ✕   │ │
│  │    (projet)     │ │    (discipline) │ │ (temporaire)              │ │
│  └─────────────────┘ └─────────────────┘ └───────────────────────────┘ │
│                                                                         │
│  [🔓 Unlock All] [🗑️ Clear Temp] [⚙️ Save Defaults]                    │
│                                                                         │
│  💡 Suggestions: pump HP > 250 | pump flow > 100 | pump area:310       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Filter Types

#### 1. Project Filter (Default: Active Project)
```typescript
interface ProjectFilter {
  type: 'project';
  value: string | null;  // null = all projects
  locked: boolean;       // User preference
}
```

**Behavior:**
- Pre-selected to current active project on load
- Can be changed to "All Projects"
- Lockable as user preference

#### 2. Discipline Quick Filters (Toggle Chips)

| Filter | Icon | MeiliSearch Filter | Color |
|--------|------|-------------------|-------|
| Electrical | ⚡ | `discipline = 'E'` | Yellow |
| Mechanical | 🔧 | `discipline = 'M'` | Blue |
| Process | 🧪 | `discipline = 'P'` | Green |
| Instrumentation | 📊 | `type = 'INSTRUMENT'` | Purple |
| Control | 🎛️ | `type IN ('PLC', 'DCS')` | Orange |

#### 3. Property-Based Suggestions

When user types a keyword, suggest property filters based on asset data:

| Keyword | Suggestions |
|---------|-------------|
| `pump` | `HP > 250`, `flow > 100 m³/h`, `area:310` |
| `motor` | `kW > 50`, `voltage:480V`, `starter:VFD` |
| `FIT` | `range:0-100`, `signal:4-20mA`, `area:*` |
| `valve` | `size > 4"`, `type:gate`, `actuator:pneumatic` |
| `cable` | `size > 4/0`, `voltage:600V`, `type:power` |

### State Management (Zustand Store)

```typescript
// stores/useSearchFiltersStore.ts

interface SearchFiltersState {
  // Locked filters (persisted)
  lockedProjectId: string | null;
  lockedDisciplines: string[];

  // Temporary filters (session only)
  tempAreas: string[];
  tempSystems: string[];
  tempTypes: string[];
  tempProperties: PropertyFilter[];

  // Actions
  setLockedProject: (id: string | null) => void;
  toggleLockedDiscipline: (disc: string) => void;
  addTempFilter: (filter: TempFilter) => void;
  removeTempFilter: (id: string) => void;
  clearTempFilters: () => void;
  saveAsDefaults: () => void;
  resetToDefaults: () => void;
}
```

### Development Tasks (Phase 2)

| Task | Effort | Priority |
|------|--------|----------|
| Create Zustand store with persistence | 2h | P1 |
| Add filter chips UI component | 3h | P1 |
| Backend: Facets endpoint (MeiliSearch native) | 1h | P1 |
| Backend: Property suggestions endpoint | 2h | P2 |
| Integrate filters in CommandPalette | 4h | P1 |
| Lock/unlock UX | 2h | P2 |
| Saved searches feature | 3h | P3 |

**Total Estimated:** ~17 hours (reduced from 21h due to MeiliSearch facets)

---

## Usage Guide

### Starting MeiliSearch

```bash
# Start with workspace infrastructure
cd workspace
docker compose up -d meilisearch

# Verify health
curl http://localhost:7700/health
# {"status":"available"}
```

### Initial Indexing

After starting MeiliSearch, trigger a full reindex:

```bash
# Via API
curl -X POST http://localhost:8001/api/v1/search/reindex

# Response
{"status":"started","message":"Reindexing started in background..."}
```

### Check Index Status

```bash
curl http://localhost:8001/api/v1/search/status

# Response
{
  "available": true,
  "engine": "meilisearch",
  "indexes": {
    "synapse_assets": {"numberOfDocuments": 3000, "isIndexing": false},
    "synapse_rules": {"numberOfDocuments": 50, "isIndexing": false},
    "synapse_cables": {"numberOfDocuments": 1500, "isIndexing": false},
    "synapse_locations": {"numberOfDocuments": 200, "isIndexing": false}
  },
  "message": "MeiliSearch is healthy"
}
```

### MeiliSearch Dashboard

Access the built-in dashboard at: `http://localhost:7700`

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-11-28 | Start with PostgreSQL + thefuzz | Simpler, sufficient for MVP |
| 2025-11-28 | Active project as default filter | Most common use case |
| 2025-11-28 | Filter persistence in localStorage | No backend needed |
| 2025-11-28 | Lock/unlock UX for preferences | User control over defaults |
| 2025-11-28 | **Implement MeiliSearch immediately** | User has 3K+ instruments, need fast search |
| 2025-11-28 | MeiliSearch with thefuzz fallback | Graceful degradation |
| 2025-11-28 | Background reindexing | Non-blocking for large datasets |

---

## Files Reference

| File | Purpose |
|------|---------|
| `workspace/docker-compose.yml` | MeiliSearch container definition |
| `backend/app/services/meilisearch_service.py` | MeiliSearch client wrapper |
| `backend/app/api/endpoints/search.py` | Search API endpoints |
| `frontend/src/services/searchService.ts` | Frontend search client |
| `frontend/src/components/ui/CommandPalette.tsx` | Search UI component |

---

**Updated:** 2025-11-28
