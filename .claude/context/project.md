# Project Context

> Auto-updated par ATLAS et DEV-TRACKER

## Plateforme

- **Nom**: AXIOM
- **Organisation**: AXoiq
- **Repository**: https://github.com/seb155/AXIOM

## Applications

| App | Status | Description |
|-----|--------|-------------|
| SYNAPSE | MVP Dec 2025 | MBSE Platform for EPCM |
| NEXUS | Phase 1.5 | Knowledge Graph + Notes |
| PRISM | Development | Enterprise Portal |
| ATLAS | Planning | AI Collaboration Env |

## Infrastructure FORGE

| Service | Container | Port |
|---------|-----------|------|
| PostgreSQL | forge-postgres | 5433 |
| Redis | forge-redis | 6379 |
| Grafana | forge-grafana | 3000 |
| Loki | forge-loki | 3100 |
| Traefik | forge-traefik | 80/443 |
| MeiliSearch | forge-meilisearch | 7700 |
| Wiki (Docsify) | forge-wiki | 3080 |

## Stack Technique

### Backend
- FastAPI 0.121+ (Python 3.10+)
- SQLAlchemy 2.0+ / Alembic
- PostgreSQL 15
- JWT + OAuth2

### Frontend
- React 19 + TypeScript
- Vite 7.2+
- Zustand (state)
- Shadcn/ui + Tailwind

## Conventions

- Conventional Commits
- Semantic Versioning
- Tests: >70% coverage
- Linting: Ruff + ESLint

## Fichiers Cles

| Fichier | Usage |
|---------|-------|
| `CLAUDE.md` | Instructions Claude Code |
| `.dev/context/project-state.md` | Etat courant |
| `.dev/testing/test-status.md` | Status tests |
| `docs/` | Documentation Docsify |
