# CORTEX - The Contextual Intelligence Engine

> **Version**: 0.5.0-dev
> **Status**: Development
> **Company**: Axoiq

## Overview

CORTEX is an autonomous AI agent for navigating codebases, planning/executing tasks, and modifying files with temporal awareness.

See full documentation: [docs/apps/cortex.md](../../docs/apps/cortex.md)

## Quick Start

### Prerequisites

- Docker & Docker Compose
- FORGE infrastructure running (PostgreSQL, Redis)
- ai-sandbox running (LiteLLM, Ollama) - optional for local models

### Development

```bash
# Start FORGE first (from AXIOM root)
cd forge && docker compose up -d forge-postgres forge-redis

# Start CORTEX
cd apps/cortex
docker compose -f docker-compose.dev.yml up --build
```

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Required variables:
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `ANTHROPIC_API_KEY` - Claude API key (primary provider)

Optional:
- `LITELLM_URL` - LiteLLM proxy URL (from ai-sandbox)
- `OLLAMA_URL` - Ollama URL for local models
- `CHROMADB_URL` - ChromaDB URL for vector storage

## Architecture

```
┌─────────────────────────────────────────────────┐
│              CORTEX ENGINE                       │
│                Port 7100                         │
├─────────────────────────────────────────────────┤
│  Orchestrator (ReAct Loop)                       │
│  ├── Job Engine                                 │
│  ├── Rule Engine                                │
│  └── Trace Engine                               │
│                                                  │
│  Context Manager                                │
│  ├── Context Blocks                             │
│  ├── Memory (HOT/WARM/COLD)                    │
│  └── Temporal Awareness                         │
│                                                  │
│  AI Router                                       │
│  └── Claude │ Gemini │ OpenAI │ Ollama          │
└─────────────────────────────────────────────────┘
```

## Ports

| Service | Port |
|---------|------|
| cortex-engine | 7100 |
| cortex-sandbox | 7101 |

## CLI Usage

```bash
# Index a repository
python -m app.cli index /path/to/repo

# Start interactive session
python -m app.cli chat /path/to/repo

# Run single task
python -m app.cli run /path/to/repo "Add validation to create_user function"
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/sessions` | POST | Create new session |
| `/api/v1/sessions/{id}/tasks` | POST | Submit task |
| `/api/v1/context/blocks` | GET/POST | Manage context blocks |
| `/ws/sessions/{id}` | WS | Real-time updates |

## Development

```bash
# Run tests
cd backend
pytest

# Run with coverage
pytest --cov=app

# Linting
ruff check . --fix
```

## Related

- [ai-sandbox](https://github.com/seb155/ai-sandbox) - LLM infrastructure
- [NEXUS](../nexus/) - UI and Knowledge Graph
- [ATLAS](../../.claude/agents/atlas.md) - Session orchestration
