# CLAUDE.md

## Quick Start

**Start every session:** `/0-new-session` (full) | `/0-next` (quick) | `/0-resume` (after /compact)

**Commands:** `/0-progress` | `/0-dashboard` | `/0-ship` | `/0-tokens` | `/0-compact`

## ATLAS 2.0

| Feature | Description |
|---------|-------------|
| Parallel Execution | Multiple Task tools in ONE message |
| Git Worktrees | Isolated dirs: `/AXIOM-worktrees/agent-{name}` |
| Sandbox Pool | 3 pre-warmed containers in FORGE |
| Layer System | Root `.claude/` + `apps/{app}/.claude/` |
| Builders | backend-builder, frontend-builder, qa-tester |

**Config:** `.atlas/config.yml` | **Docs:** `.atlas/ATLAS-2.0-PLAN.md`

## Token Optimization

**Workflow:** `/0-tokens` (check) → `/0-compact` (at 50%) → `/0-resume` (restore)

- `/compact` at ~50% capacity, then `/0-resume`
- Max 5 concurrent agents (Sonnet builders, Haiku QA)
- Runtime excluded via `.claudeignore`
- MCP servers: `/0-mcp` to manage (can use 30k+ tokens)

## Conventions

**Code:**
- Python: `snake_case` files, `PascalCase` classes
- TypeScript: `PascalCase.tsx` components, `camelCase.ts` utils
- Database: `plural_snake_case` tables

**Rules:** Use spaces/colons, NEVER underscores
- OK: `FIRM: Centrifugal Pumps require Electric Motor`
- BAD: `firm_motor_rule`

## Key URLs

| App | URL |
|-----|-----|
| SYNAPSE | https://synapse.axoiq.com |
| NEXUS | https://nexus.axoiq.com |
| Grafana | https://grafana.axoiq.com |

**Login:** admin@aurumax.com / admin123!

## Essential Commands

```bash
# Backend
pytest && ruff check . --fix

# Frontend
npm run test && npm run build

# Docker
docker logs synapse-backend -f --tail 100
```

## Infrastructure Policy

**BEFORE any port/network operation:** Read `.dev/infra/registry.yml`

## Extended Documentation

| Topic | File |
|-------|------|
| Platform & URLs | @.claude/docs/platform.md |
| Dev Commands | @.claude/docs/commands.md |
| Infrastructure | @.claude/docs/infra.md |
| AI Agents | @.claude/docs/agents.md |
| ATLAS Config | @.atlas/config.yml |

## Key Files

| Need | File |
|------|------|
| Project state | `.dev/context/project-state.md` |
| Test tracking | `.dev/testing/test-status.md` |
| Credentials | `.dev/context/credentials.md` |
| URL Registry | `.dev/infra/url-registry.yml` |

---
**Repository:** https://github.com/seb155/AXIOM
