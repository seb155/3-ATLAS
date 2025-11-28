<p align="center">
  <h1 align="center">AXIOM</h1>
  <p align="center">
    <strong>AXoiq Enterprise Platform</strong>
  </p>
  <p align="center">
    Unified development ecosystem for engineering, knowledge management, and AI collaboration
  </p>
</p>

<p align="center">
  <a href="#applications">Applications</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#documentation">Documentation</a>
</p>

---

## Overview

**AXIOM** is a comprehensive enterprise platform built with modern technologies, designed for engineering workflows, knowledge management, and AI-assisted development.

| Application | Description | Status |
|-------------|-------------|--------|
| **SYNAPSE** | Model-Based Systems Engineering (MBSE) Platform | MVP Dec 2025 |
| **NEXUS** | Personal Knowledge Graph & Notes Portal | Phase 1.5 |
| **PRISM** | Enterprise Dashboard & Project Portal | Development |
| **ATLAS** | AI Collaboration Environment | Planning |

**Infrastructure:** **FORGE** - Shared development infrastructure (PostgreSQL, Redis, Traefik, Logging)

---

## Applications

### SYNAPSE - MBSE Platform
> Engineering automation for EPCM projects

- Asset & Instrument management
- Rule engine with event sourcing
- CSV/Excel import/export
- Graph-based metamodel visualization
- Package generation for deliverables

**Tech:** FastAPI • React 19 • PostgreSQL • SQLAlchemy • Zustand

### NEXUS - Knowledge Graph
> Personal & team knowledge management

- Notes with Markdown support
- Wiki-style documentation
- Task management
- 3D Graph visualization
- 13 pre-built themes

**Tech:** React 19 • FastAPI • Zustand • Tailwind CSS

### PRISM - Enterprise Portal
> Project dashboard and team collaboration

- Project overview & metrics
- Team management
- Infrastructure monitoring
- Technical debt tracking

**Tech:** React 19 • TypeScript • Tailwind CSS

### ATLAS - AI Collaboration
> AI-assisted development environment

- Multi-agent workflows
- Context-aware assistance
- Knowledge graph integration
- Real-time collaboration

**Status:** Planning phase

---

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 20+
- Python 3.11+
- PowerShell (Windows)

### 1. Clone the repository

```bash
git clone https://github.com/seb155/AXIOM.git
cd AXIOM
```

### 2. Start the platform

```powershell
# Start FORGE infrastructure + SYNAPSE
.\dev.ps1
```

### 3. Access applications

| Application | URL |
|-------------|-----|
| SYNAPSE | http://localhost:4000 |
| NEXUS | http://localhost:5173 |
| pgAdmin | http://localhost:5050 |
| Grafana | http://localhost:3000 |
| Prisma Studio | http://localhost:5555 |

**Default credentials:** `admin@axoiq.com` / `admin123!`

---

## Architecture

```
AXIOM/
├── apps/
│   ├── synapse/          # MBSE Platform
│   │   ├── backend/      # FastAPI + SQLAlchemy
│   │   └── frontend/     # React 19 + Vite
│   ├── nexus/            # Knowledge Graph
│   ├── prism/            # Enterprise Portal
│   └── atlas/            # AI Collaboration
│
├── forge/                # Shared Infrastructure
│   ├── docker-compose.yml
│   ├── config/           # Service configs
│   └── databases/        # Data persistence
│
├── docs/                 # Documentation
├── .agent/               # AI Workflows
└── .dev/                 # Development Context
```

### Technology Stack

**Backend**
- FastAPI 0.121+
- Python 3.11+
- SQLAlchemy 2.0+
- PostgreSQL 15
- Redis 7
- Alembic (migrations)

**Frontend**
- React 19
- TypeScript (strict)
- Vite 7.2+
- Zustand (state)
- Shadcn/ui + Radix UI
- Tailwind CSS 4+

**Infrastructure**
- Docker Compose
- Traefik (reverse proxy)
- Loki + Grafana (logging)
- Prisma Studio

---

## FORGE Infrastructure

Shared services available to all applications:

| Service | Container | Port | Description |
|---------|-----------|------|-------------|
| PostgreSQL | `forge-postgres` | 5433 | Main database |
| Redis | `forge-redis` | 6379 | Cache & sessions |
| pgAdmin | `forge-pgadmin` | 5050 | Database admin UI |
| Prisma Studio | `forge-prisma` | 5555 | Schema viewer |
| Grafana | `forge-grafana` | 3000 | Log visualization |
| Loki | `forge-loki` | 3100 | Log aggregation |
| MeiliSearch | `forge-meilisearch` | 7700 | Full-text search |

```powershell
# Start FORGE only
cd forge
docker-compose up -d

# Start specific services
docker-compose up -d forge-postgres forge-redis
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [CLAUDE.md](./CLAUDE.md) | AI assistant guide |
| [CHANGELOG.md](./CHANGELOG.md) | Version history |
| [docs/](./docs/) | Full documentation |
| [.agent/workflows/](./.agent/workflows/) | Development workflows |
| [.dev/](./.dev/) | Development context & journals |

---

## Development

### Running Tests

```bash
# Backend tests
cd apps/synapse/backend
pytest --cov=app

# Frontend tests
cd apps/synapse/frontend
npm run test
```

### Code Quality

```bash
# Backend
ruff check .
black .

# Frontend
npm run lint
npm run type-check
```

---

## License

Proprietary - All rights reserved

---

<p align="center">
  <sub>Built with precision by <strong>AXoiq</strong></sub>
</p>
