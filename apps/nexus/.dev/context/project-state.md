# NEXUS Project State

**Last Updated:** 2025-11-29
**Version:** v0.2.0
**Phase:** 2.0 - Notes/Wiki System + TriliumNext Integration

## Current Status

### Completed (Phase 2.0)

- [x] Notes CRUD API (create, read, update, delete)
- [x] Notes tree structure with parent/child relationships
- [x] Full-text search via PostgreSQL TSVECTOR
- [x] Wiki-style [[links]] with backlinks
- [x] TipTap rich text editor in frontend
- [x] Authentication with workspace SSO
- [x] **TriliumNext Integration** (bidirectional sync)

### TriliumNext Integration Details

| Feature | Status | Notes |
|---------|--------|-------|
| ETAPI Connection | Done | v0.92.4 connected |
| Import from Trilium | Done | Recursive import working |
| Push to Trilium | Done | Create/update notes |
| Sync mapping table | Done | `trilium_sync` table |
| Full bidirectional sync | Done | `/sync/full` endpoint |

### In Progress

- [ ] Frontend UI for Trilium sync
- [ ] Background sync worker
- [ ] Conflict detection UI

### Planned (Phase 2.5+)

- [ ] pgvector for AI embeddings
- [ ] react-force-graph-3d visualization
- [ ] Semantic search
- [ ] AI chat with notes context

## Architecture

```
Frontend (React 19)
    │
    ▼
Backend (FastAPI)
    │
    ├──► PostgreSQL (nexus DB)
    │       ├── notes
    │       ├── tags
    │       ├── wiki_links
    │       └── trilium_sync
    │
    ├──► Redis (caching)
    │
    └──► TriliumNext (ETAPI)
            └── External notes source
```

## Key Decisions

1. **Trilium as source of truth** - NEXUS extends Trilium rather than replacing it
2. **Async sync** - aiohttp for non-blocking Trilium API calls
3. **UUID mapping** - Each synced note has both NEXUS UUID and Trilium 12-char ID
4. **Soft delete** - Notes use `deleted_at` timestamp, not hard delete

## Environment

- **Backend:** Docker container `nexus-backend`
- **Frontend:** Docker container `nexus-frontend`
- **Database:** `workspace-postgres` (nexus DB)
- **Auth:** `workspace_auth.users` schema (shared SSO)
- **Trilium:** https://notes.s-gagnon.com (external)

## Quick Commands

```bash
# Start NEXUS
cd apps/nexus && docker compose -f docker-compose.dev.yml up -d

# View logs
docker logs nexus-backend -f

# Run migrations
docker exec nexus-backend alembic upgrade head

# Test Trilium connection
curl -s http://localhost:8000/api/v1/trilium/status \
  -H "Authorization: Bearer <token>"
```
