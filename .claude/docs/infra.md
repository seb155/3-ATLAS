# FORGE Infrastructure

## Services

| Service | Container | Port |
|---------|-----------|------|
| PostgreSQL | `forge-postgres` | 5433 |
| Redis | `forge-redis` | 6379 |
| pgAdmin | `forge-pgadmin` | 5050 |
| Prisma Studio | `forge-prisma` | 5555 |
| Grafana | `forge-grafana` | 3000 |
| MeiliSearch | `forge-meilisearch` | 7700 |
| Docs (Docsify) | `forge-wiki` | 3080 |
| Traefik | `forge-traefik` | 80, 443, 8888 |

## Port Allocation Ranges

| Application | Range | Allocated | Available |
|-------------|-------|-----------|-----------|
| **FORGE** | 3000-3999 | 9 ports | 991 ports |
| **SYNAPSE** | 4000-4999 | 2 ports | 998 ports |
| **NEXUS** | 5000-5999 | 2 ports | 998 ports |
| **APEX** | 6000-6999 | 0 ports | 1000 ports |
| **CORTEX** | 7000-7999 | 2 ports | 998 ports |

**Rule**: Each app has dedicated 1000-port range. No conflicts.

## Infrastructure Management

### MANDATORY POLICY

**BEFORE any port/network/Docker operation:**
```
Read file: .dev/infra/registry.yml
```

**DO NOT:**
- Guess port numbers
- Assume network configuration
- Create docker-compose without checking registry

### CLI Tools

```powershell
.\.dev\scripts\axiom.ps1 status    # Quick status
.\.dev\scripts\axiom.ps1 ports     # Port allocations
.\.dev\scripts\axiom.ps1 start synapse
.\.dev\scripts\axiom.ps1 validate
.\.dev\scripts\axiom.ps1 health
```

### AI Agent Tools

**Quick Status:** `skill: "infra"`

**Complex Operations:** `Task tool with subagent_type="devops-manager"`

Use DevOps Manager for:
- Adding new services
- Diagnosing problems
- Validating configurations
- Resolving conflicts

## Key Files

| File | Purpose |
|------|---------|
| `.dev/infra/registry.yml` | Central registry (SINGLE SOURCE OF TRUTH) |
| `.dev/infra/infrastructure.md` | Complete documentation |
| `.dev/infra/CHANGELOG.md` | Change history |
| `.claude/agents/devops-manager.md` | DevOps Manager agent |
