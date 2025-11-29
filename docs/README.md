# AXIOM Platform Documentation

> **Unified Enterprise Platform for Engineering, Knowledge & AI Collaboration**

Welcome to AXIOM! This documentation covers all applications and infrastructure.

---

## Quick Navigation

| I want to... | Go to... |
|:---|:---|
| **Get started quickly** | [Quick Start](#quick-start) |
| **Understand the architecture** | [Architecture Overview](./getting-started/03-architecture-overview.md) |
| **Set up my environment** | [Installation](./getting-started/01-installation.md) |
| **Learn about SYNAPSE** | [SYNAPSE Guide](./apps/synapse.md) |
| **Use the AI agents** | [AI Agents Overview](./developer-guide/ai-agents-overview.md) |
| **Run tests** | [Testing Guide](./developer-guide/08-testing.md) |
| **Manage infrastructure** | [Infrastructure Guide](./infrastructure/README.md) |

---

## Platform Overview

**AXIOM** is an integrated enterprise platform containing four specialized applications:

| Application | Port | Purpose | Status |
|:---|:---:|:---|:---:|
| **SYNAPSE** | 4000 | MBSE Platform - Engineering automation | MVP v0.2.5 |
| **NEXUS** | 5173 | Knowledge Graph - Notes, Wiki, Tasks | Phase 1.5 |
| **PRISM** | 6000 | Enterprise Dashboard | Planning |
| **ATLAS** | 7000 | AI Collaboration Environment | Planning |

All applications share the **FORGE** infrastructure (PostgreSQL, Redis, Grafana, etc.)

---

## Quick Start

```powershell
# Clone the repository
git clone https://github.com/seb155/AXIOM.git
cd AXIOM

# Start everything
.\dev.ps1

# Access applications
# SYNAPSE: http://localhost:4000
# Grafana: http://localhost:3000
```

**Credentials:**
- SYNAPSE: `admin@axoiq.com` / `admin123!`
- Grafana: `admin` / `admin`

---

## Documentation Structure

### Getting Started

| Document | Description |
|:---|:---|
| [Installation](./getting-started/01-installation.md) | Setup in 5 minutes |
| [First Steps](./getting-started/02-first-steps.md) | Login, navigate, explore |
| [Architecture Overview](./getting-started/03-architecture-overview.md) | System design |

### Applications

#### SYNAPSE - MBSE Platform

Engineering data management with rule engines, impact analysis, and package generation.

| Document | Description |
|:---|:---|
| [SYNAPSE Overview](./apps/synapse.md) | Application guide |
| [Rule Engine](./developer-guide/rule-engine-event-sourcing.md) | Rule engine deep dive |
| [Workflow Engine](./developer-guide/workflow-engine.md) | Event sourcing & audit |
| [Project Structure](./developer-guide/01-project-structure.md) | Code organization |

#### Other Applications

| Application | Documentation |
|:---|:---|
| [NEXUS](./apps/nexus.md) | Knowledge Graph - Notes, Wiki |
| [PRISM](./apps/prism.md) | Enterprise Dashboard |
| [ATLAS](./apps/atlas.md) | AI Collaboration |

### Infrastructure

| Document | Description |
|:---|:---|
| [Infrastructure Overview](./infrastructure/README.md) | Complete infrastructure guide |
| [CLI Reference](./infrastructure/cli-reference.md) | axiom.ps1 command reference |
| [For Developers](./infrastructure/for-developers.md) | Daily workflows |

### Developer Guide

| Document | Description |
|:---|:---|
| [Project Structure](./developer-guide/01-project-structure.md) | Code organization |
| [Testing](./developer-guide/08-testing.md) | Test guide |
| [Deployment](./developer-guide/06-deployment.md) | Deployment guide |
| [Tools Setup](./developer-guide/tools-setup.md) | Development tools |
| [AI Agents Overview](./developer-guide/ai-agents-overview.md) | AI agents system |
| [AI Agents System](./developer-guide/ai-agents-system.md) | Technical details |

### Reference

| Document | Description |
|:---|:---|
| [Asset Lifecycle](./reference/asset-lifecycle.md) | Asset states & transitions |
| [Rule Engine API](./reference/rule-engine-api.md) | API reference |
| [Package Deliverables](./reference/package-deliverables.md) | Export templates |
| [Design System](./reference/design-system.md) | UI components |
| [Logging Infrastructure](./reference/logging-infrastructure.md) | Logs & monitoring |

### Workflows

| Document | Description |
|:---|:---|
| [Using DevConsole](./workflows/using-devconsole.md) | Real-time logs |
| [Creating Baselines](./workflows/creating-baselines.md) | Baseline management |
| [Package Generation](./workflows/package-generation.md) | Export workflows |
| [Impact Analysis](./workflows/using-impact-analysis.md) | Change tracking |

### Contributing

| Document | Description |
|:---|:---|
| [Code Guidelines](./contributing/code-guidelines.md) | Standards & conventions |
| [Git Workflow](./contributing/git-workflow.md) | Branches, PRs, commits |

---

## FORGE Infrastructure

Shared services available to all applications:

| Service | Port | URL |
|:---|:---:|:---|
| PostgreSQL | 5433 | `localhost:5433` |
| Redis | 6379 | `localhost:6379` |
| pgAdmin | 5050 | http://localhost:5050 |
| Prisma Studio | 5555 | http://localhost:5555 |
| Grafana | 3000 | http://localhost:3000 |
| Loki | 3100 | http://localhost:3100 |
| MeiliSearch | 7700 | http://localhost:7700 |
| Traefik | 80, 443, 8888 | http://localhost:8888 |

**Infrastructure Management:**

```powershell
# Quick status
.\.dev\scripts\axiom.ps1 status

# View port allocations
.\.dev\scripts\axiom.ps1 ports

# Start services
.\.dev\scripts\axiom.ps1 start synapse

# Check health
.\.dev\scripts\axiom.ps1 health
```

**See:** [Infrastructure Documentation](./infrastructure/) for complete guide

---

## AI Agents System

AXIOM includes 18+ specialized AI agents:

| Layer | Agents | Role |
|:---|:---|:---|
| **Orchestrators** | ATLAS, GENESIS, BRAINSTORM | Strategy & coordination |
| **Builders** | Backend, Frontend, DevOps, Architect | Implementation |
| **Validators** | QA-Tester, Issue-Reporter | Quality assurance |
| **Trackers** | Dev-Tracker, Git-Manager | Progress tracking |
| **Planners** | Debugger, Planner, UX-Designer | Analysis & planning |

**Quick Commands:**

| Command | Description |
|:---|:---|
| `/0-new-session` | Start new session (full context) |
| `/0-next` | Continue next task |
| `/0-progress` | View roadmap |
| `/0-ship` | Git workflow (test + commit + push) |

**See:** [AI Agents Overview](./developer-guide/ai-agents-overview.md) for details

---

## Internal Documentation

For detailed architecture and development context, see:

| Document | Location |
|:---|:---|
| Full Architecture | [.dev/ARCHITECTURE.md](../.dev/ARCHITECTURE.md) |
| Project State | [.dev/context/project-state.md](../.dev/context/project-state.md) |
| Port Registry | [.dev/infra/registry.yml](../.dev/infra/registry.yml) |
| AI Instructions | [CLAUDE.md](../CLAUDE.md) |

---

## Version Information

**Platform Version:** 0.2.5 (Atlas Orchestration System)
**Last Updated:** 2025-11-29
**Repository:** [github.com/seb155/AXIOM](https://github.com/seb155/AXIOM)
