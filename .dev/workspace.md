# AXIOM Workspace

> Auto-generated workspace map for AI navigation

## Project Structure

```
AXIOM/ (parent)
├── .dev/                      # Parent context & shared resources
├── apps/
│   ├── synapse/.dev/          # SYNAPSE - MBSE Platform [MVP 85%]
│   ├── nexus/.dev/            # NEXUS - Knowledge Portal [Phase 1.5 40%]
│   ├── atlas/.dev/            # ATLAS - AI OS [Complete 100%]
│   ├── apex/.dev/             # APEX - Enterprise Portal [Planning 5%]
│   ├── cortex/.dev/           # CORTEX - Memory Engine [Design 10%]
│   └── echo/.dev/             # ECHO - Voice Assistant
└── forge/.dev/                # FORGE - Infrastructure [Stable 95%]
```

## Children Projects

| Project | Path | Status | Progress | Priority |
|---------|------|--------|----------|----------|
| SYNAPSE | `apps/synapse/.dev` | Active | 85% | 1 |
| NEXUS | `apps/nexus/.dev` | Development | 40% | 2 |
| ATLAS | `apps/atlas/.dev` | Complete | 100% | 1 |
| APEX | `apps/apex/.dev` | Planning | 5% | 4 |
| CORTEX | `apps/cortex/.dev` | Design | 10% | 3 |
| ECHO | `apps/echo/.dev` | Development | - | - |
| FORGE | `forge/.dev` | Stable | 95% | 0 |

## Shared Resources

| Resource | Location | Purpose |
|----------|----------|---------|
| Credentials | `context/credentials.md` | DB, services, admin passwords |
| Infrastructure | `infra/registry.yml` | Port registry, networks |
| URL Registry | `infra/url-registry.yml` | All service URLs |
| Decisions | `decisions/` | Architecture Decision Records |
| Apps Registry | `ai/active-apps.json` | App status & progress |

## AI Navigation

```bash
# View this workspace from anywhere in AXIOM
# AI reads .dev-manifest.json automatically

# Start session in specific app
cd apps/synapse && /0-new-session

# From child, access parent resources
# Manifest declares inherit_from_parent: ["credentials", "infrastructure"]
```

## Quick Commands

| Command | Purpose |
|---------|---------|
| `/0-new-session` | Start with workspace overview |
| `/0-progress` | View all apps progression |
| `/0-dashboard` | Current session status |

## Infrastructure

| Service | Container | Port |
|---------|-----------|------|
| PostgreSQL | `forge-postgres` | 5433 |
| Redis | `forge-redis` | 6379 |
| Traefik | `forge-traefik` | 80, 443 |
| Grafana | `forge-grafana` | 3000 |

---

**Last Updated:** 2025-12-01

*This file is auto-generated. Edit `.dev-manifest.json` to update structure.*
