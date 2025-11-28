# AXIOM Platform Migration Guide

> Documentation of the migration from multiple repositories to the unified AXIOM platform.
> **Date:** November 28, 2025

---

## Overview

The AXIOM platform was created by consolidating multiple separate projects into a unified monorepo structure. This document details the migration process, naming conventions, and architectural decisions.

---

## Migration Summary

### Repository Consolidation

| Original Location | New Location | Description |
|-------------------|--------------|-------------|
| `D:\Projects\EPCB-Tools\` | `D:\Projects\AXIOM\` | Main monorepo root |
| `D:\Projects\EPCB-Tools\apps\synapse\` | `AXIOM\apps\synapse\` | MBSE Platform (unchanged) |
| `D:\Projects\nexus\` | `AXIOM\apps\nexus\` | Knowledge Graph (integrated) |
| `D:\Projects\EPCB-Tools\apps\portal\` | `AXIOM\apps\prism\` | Enterprise Portal (renamed) |
| `D:\Projects\EPCB-Tools\workspace\` | `AXIOM\forge\` | Infrastructure (renamed) |
| (new) | `AXIOM\apps\atlas\` | AI Collaboration (created) |

### Archived Repositories

Original repositories were moved to `D:\Projects\9-Archive\`:
- `EPCB-Tools/`
- `nexus/`
- `enterprise-monorepo-template/`
- `EPCB-App-Template/`

---

## Naming Convention

### Platform Name: AXIOM

**AXIOM** represents the unified AXoiq enterprise platform, containing all applications and shared infrastructure.

### Application Names

| Name | Meaning | Purpose |
|------|---------|---------|
| **SYNAPSE** | Neural connections | MBSE Platform - connects engineering data |
| **NEXUS** | Central connection point | Knowledge Graph - connects information |
| **PRISM** | Light refraction | Enterprise Portal - provides different views |
| **ATLAS** | Greek titan / Map collection | AI Collaboration - maps knowledge |
| **FORGE** | Metal workshop | Infrastructure - builds foundation |

### Docker Service Naming

All infrastructure services use the `forge-` prefix:

| Old Name | New Name |
|----------|----------|
| `workspace-postgres` | `forge-postgres` |
| `workspace-redis` | `forge-redis` |
| `workspace-network` | `forge-network` |
| `workspace-loki` | `forge-loki` |
| `workspace-grafana` | `forge-grafana` |
| `workspace-promtail` | `forge-promtail` |
| `workspace-pgadmin` | `forge-pgadmin` |
| `workspace-prisma` | `forge-prisma` |
| `workspace-meilisearch` | `forge-meilisearch` |
| `workspace-traefik` | `forge-traefik` |
| `workspace-homepage` | (removed - replaced by PRISM) |

---

## Architecture Changes

### Before: Multiple Repositories

```
D:\Projects\
├── EPCB-Tools/                 # Main project repo
│   ├── apps/
│   │   ├── synapse/            # MBSE Platform
│   │   └── portal/             # Dev Portal
│   ├── workspace/              # Infrastructure
│   ├── docs/
│   ├── .agent/
│   └── .dev/
│
├── nexus/                      # Separate repo
│   ├── backend/
│   └── frontend/
│
├── enterprise-monorepo-template/  # Template repo
└── EPCB-App-Template/             # Another template
```

### After: Unified AXIOM Platform

```
D:\Projects\
├── AXIOM/                      # Unified platform
│   ├── apps/
│   │   ├── synapse/            # MBSE Platform
│   │   ├── nexus/              # Knowledge Graph
│   │   ├── prism/              # Enterprise Portal
│   │   └── atlas/              # AI Collaboration
│   │
│   ├── forge/                  # Shared Infrastructure
│   │   ├── docker-compose.yml
│   │   ├── config/
│   │   ├── databases/
│   │   └── prisma/
│   │
│   ├── docs/                   # Documentation
│   ├── .agent/                 # AI Workflows
│   ├── .dev/                   # Dev Context
│   │
│   ├── CLAUDE.md
│   ├── CHANGELOG.md
│   ├── README.md
│   ├── dev.ps1
│   └── stop.ps1
│
├── HomeAssistant/              # Unchanged
└── 9-Archive/                  # Archived old repos
```

---

## Files Modified

### Docker Compose Files

**Renamed services in 43 files:**
- `forge/docker-compose.yml`
- `forge/docker-compose.traefik.yml`
- `forge/docker-compose.traefik-labels.yml`
- `apps/synapse/docker-compose.dev.yml`
- `apps/synapse/docker-compose.prod.yml`
- `apps/nexus/docker-compose.dev.yml`
- And 37 more documentation/config files

### Removed Files

| File | Reason |
|------|--------|
| `forge/docker-compose.homepage.yml` | Replaced by PRISM |
| `forge/docker-compose.owner-portal.yml` | Obsolete |
| `forge/docker-compose.dns.yml` | Not needed |
| `forge/homepage/` directory | Replaced by PRISM |

### New Files Created

| File | Purpose |
|------|---------|
| `AXIOM/CHANGELOG.md` | Version history |
| `AXIOM/README.md` | Platform overview |
| `AXIOM/CLAUDE.md` | AI assistant guide |
| `AXIOM/.gitignore` | Git ignore rules |
| `AXIOM/dev.ps1` | Start script |
| `AXIOM/stop.ps1` | Stop script |
| `AXIOM/package.json` | Workspace config |
| `apps/atlas/README.md` | ATLAS documentation |
| `docs/index.html` | Docsify configuration |
| `docs/_sidebar.md` | Documentation navigation |
| `docs/apps/*.md` | Application documentation |
| `docs/.nojekyll` | GitHub Pages compatibility |

---

## Documentation System

### Docsify Setup

The AXIOM platform uses **Docsify** for documentation, running as a Docker service in FORGE.

**Features:**
- Dark theme with AXIOM branding
- Full-text search
- Automatic sidebar navigation
- Syntax highlighting for code blocks
- Application badges (SYNAPSE, NEXUS, PRISM, ATLAS, FORGE)

**Access:** http://localhost:3080

**Files:**
```
docs/
├── index.html          # Docsify configuration
├── _sidebar.md         # Navigation menu
├── README.md           # Home page
├── .nojekyll           # GitHub Pages compatibility
├── MIGRATION-AXIOM.md  # This file
├── apps/               # Application docs
│   ├── synapse.md
│   ├── nexus.md
│   ├── prism.md
│   └── atlas.md
├── getting-started/    # Getting started guides
├── developer-guide/    # Developer documentation
├── reference/          # Reference documentation
├── workflows/          # Workflow guides
└── contributing/       # Contribution guidelines
```

**Local Development:**
- Edit Markdown files in `docs/`
- Changes appear immediately (hot reload)
- Doc server runs in `forge-docs` container

---

## Configuration Changes

### Email Addresses
- `admin@example.com` → `admin@axoiq.com`

### Environment Variables
- `MEILI_MASTER_KEY` default: `synapse_dev_key_change_in_prod` → `axiom_dev_key_change_in_prod`

### Network Names
- `workspace-network` → `forge-network`

### Volume Paths
- `/workspace/prisma` → `/forge/prisma`

---

## FORGE Infrastructure Services

| Service | Container | Port | Purpose |
|---------|-----------|------|---------|
| PostgreSQL | `forge-postgres` | 5433 | Main database |
| Redis | `forge-redis` | 6379 | Cache & sessions |
| pgAdmin | `forge-pgadmin` | 5050 | Database admin |
| Prisma Studio | `forge-prisma` | 5555 | Schema viewer |
| Grafana | `forge-grafana` | 3000 | Visualization |
| Loki | `forge-loki` | 3100 | Log aggregation |
| Promtail | `forge-promtail` | - | Log collection |
| MeiliSearch | `forge-meilisearch` | 7700 | Full-text search |
| Documentation | `forge-docs` | 3080 | Docsify doc server |

---

## Docker Cleanup

During migration, the following cleanup was performed:

```powershell
# Stop and remove all containers
docker stop $(docker ps -aq)
docker rm $(docker ps -aq)

# Remove obsolete networks
docker network rm workspace-network synapse_default

# Full prune (recovered 27 GB)
docker system prune -af --volumes
```

---

## Git History

### Commits

1. `370cce1` - Initial commit: AXIOM Platform structure
2. `60dfdb9` - docs: Add professional README
3. `bf0b308` - refactor: Rename workspace to forge infrastructure
4. `acdfed1` - chore: Clean up FORGE infrastructure

### Repository

- **URL:** https://github.com/seb155/AXIOM
- **Visibility:** Private
- **Branch:** master

---

## Verification Checklist

After migration, verify:

- [ ] All apps can start (`.\dev.ps1`)
- [ ] FORGE services are accessible
- [ ] Database connections work (`forge-postgres`)
- [ ] No references to `workspace-` remain in code
- [ ] Git repository is properly initialized
- [ ] All documentation is updated

---

## Rollback Plan

If needed, original repositories are preserved in `9-Archive/`:

```powershell
# Restore original structure (if needed)
mv D:\Projects\9-Archive\EPCB-Tools D:\Projects\
mv D:\Projects\9-Archive\nexus D:\Projects\
```

---

**Migration completed:** November 28, 2025
**Performed by:** Claude Code + User
