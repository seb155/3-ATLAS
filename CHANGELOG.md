# Changelog

All notable changes to the AXIOM Platform will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2025-11-28

### Added
- **Docsify Wiki Server** (`forge-wiki` on port 3080)
  - Dark theme with AXIOM branding
  - Full-text search
  - Application badges (SYNAPSE, NEXUS, PRISM, ATLAS, FORGE)
  - Sidebar navigation with all documentation
- **Application Documentation**
  - `docs/apps/synapse.md` - MBSE Platform documentation
  - `docs/apps/nexus.md` - Knowledge Graph documentation
  - `docs/apps/prism.md` - Enterprise Portal documentation
  - `docs/apps/atlas.md` - AI Collaboration documentation
- **Docsify Configuration**
  - `docs/index.html` - Docsify setup with plugins
  - `docs/_sidebar.md` - Navigation structure
  - `docs/.nojekyll` - GitHub Pages compatibility

### Changed
- Updated `docs/README.md` as AXIOM platform home page
- Updated `forge/docker-compose.yml` with `forge-wiki` service

---

## [1.0.0] - 2025-11-28

### Added
- **AXIOM Platform** - New unified monorepo structure for AXoiq enterprise suite
- **ATLAS** - New AI Collaboration Environment (planning phase)
- **Professional README** with platform overview and quick start guide
- **Comprehensive .gitignore** for all project types

### Changed
- **Repository Migration**
  - EPCB-Tools → AXIOM (monorepo root)
  - EPCB-Tools/apps/synapse → AXIOM/apps/synapse
  - nexus/ → AXIOM/apps/nexus
  - EPCB-Tools/apps/portal → AXIOM/apps/prism (renamed)
  - EPCB-Tools/workspace → AXIOM/forge (renamed)

- **Infrastructure Renaming** (workspace → forge)
  - `workspace-postgres` → `forge-postgres`
  - `workspace-redis` → `forge-redis`
  - `workspace-network` → `forge-network`
  - `workspace-loki` → `forge-loki`
  - `workspace-grafana` → `forge-grafana`
  - `workspace-promtail` → `forge-promtail`
  - `workspace-pgadmin` → `forge-pgadmin`
  - `workspace-prisma` → `forge-prisma`
  - `workspace-meilisearch` → `forge-meilisearch`

- **Configuration Updates**
  - pgAdmin email: `admin@example.com` → `admin@axoiq.com`
  - MeiliSearch key prefix: `synapse_dev_key` → `axiom_dev_key`
  - Prisma working directory: `/workspace/prisma` → `/forge/prisma`

### Removed
- `forge/docker-compose.homepage.yml` - Replaced by PRISM
- `forge/docker-compose.owner-portal.yml` - Obsolete
- `forge/docker-compose.dns.yml` - Obsolete
- `forge/homepage/` directory - Replaced by PRISM

### Archived
- Original repositories moved to `9-Archive/`:
  - `EPCB-Tools/`
  - `nexus/`
  - `enterprise-monorepo-template/`
  - `EPCB-App-Template/`

---

## Application Versions

| Application | Version | Status |
|-------------|---------|--------|
| SYNAPSE | v0.2.2-dev | MVP Dec 2025 |
| NEXUS | v0.1.0-alpha | Phase 1.5 |
| PRISM | v0.1.0 | Development |
| ATLAS | v0.0.1 | Planning |

---

## Migration Summary

### Before (Multiple Repos)
```
D:\Projects\
├── EPCB-Tools/           # Main project
│   ├── apps/synapse/
│   ├── apps/portal/
│   └── workspace/
├── nexus/                # Separate repo
├── enterprise-monorepo-template/
└── EPCB-App-Template/
```

### After (Unified AXIOM)
```
D:\Projects\
├── AXIOM/                # Unified platform
│   ├── apps/
│   │   ├── synapse/      # MBSE Platform
│   │   ├── nexus/        # Knowledge Graph
│   │   ├── prism/        # Enterprise Portal
│   │   └── atlas/        # AI Collaboration
│   ├── forge/            # Shared Infrastructure
│   ├── docs/
│   ├── .agent/
│   └── .dev/
├── HomeAssistant/        # Unchanged
└── 9-Archive/            # Old repos
```
