# AXIOM Platform Documentation

> **Unified Enterprise Platform for Engineering, Knowledge & AI Collaboration**

Welcome to AXIOM! This documentation covers all applications and infrastructure.

---

## Platform Overview

**AXIOM** is an integrated enterprise platform containing four specialized applications:

| Application | Purpose | Status |
|-------------|---------|--------|
| **SYNAPSE** | Model-Based Systems Engineering (MBSE) | Production |
| **NEXUS** | Knowledge Graph & Personal Portal | Production |
| **PRISM** | Enterprise Portal & Dashboard | Development |
| **ATLAS** | AI Collaboration Environment | Planning |

All applications share the **FORGE** infrastructure (PostgreSQL, Redis, Grafana, etc.)

---

## Quick Start

```powershell
# Clone the repository
git clone https://github.com/seb155/AXIOM.git
cd AXIOM

# Start FORGE infrastructure
.\dev.ps1

# Access applications
# SYNAPSE: http://localhost:8080
# NEXUS:   http://localhost:3001
# PRISM:   http://localhost:3002
```

---

## Documentation Structure

### Getting Started
- [Installation](getting-started/01-installation.md) - Setup in 5 minutes
- [First Steps](getting-started/02-first-steps.md) - Login, navigate, explore
- [Architecture Overview](getting-started/03-architecture-overview.md) - System design

### Applications

#### SYNAPSE - MBSE Platform
Engineering data management with rule engines, impact analysis, and package generation.
- [Project Structure](developer-guide/01-project-structure.md)
- [Rule Engine](developer-guide/rule-engine-event-sourcing.md)
- [Workflow Engine](developer-guide/workflow-engine.md)

#### NEXUS - Knowledge Graph
Personal knowledge management with graph visualization and search.
- Coming soon

#### PRISM - Enterprise Portal
Unified dashboard for project management and analytics.
- Coming soon

#### ATLAS - AI Collaboration
AI-powered development and collaboration tools.
- Coming soon

### Infrastructure Management
- [Infrastructure Overview](infrastructure/README.md) - Complete infrastructure guide
- [CLI Reference](infrastructure/cli-reference.md) - axiom.ps1 command reference
- [For Developers](infrastructure/for-developers.md) - Daily workflows and best practices

### Developer Guide
- [Tools Setup](developer-guide/tools-setup.md)
- [Testing](developer-guide/08-testing.md)
- [Deployment](developer-guide/06-deployment.md)

### Reference
- [Design System](reference/design-system.md)
- [Asset Lifecycle](reference/asset-lifecycle.md)
- [Rule Engine API](reference/rule-engine-api.md)
- [Logging Infrastructure](reference/logging-infrastructure.md)

### Workflows
- [Using DevConsole](workflows/using-devconsole.md)
- [Creating Baselines](workflows/creating-baselines.md)
- [Package Generation](workflows/package-generation.md)
- [Impact Analysis](workflows/using-impact-analysis.md)

---

## FORGE Infrastructure

Shared services available to all applications:

| Service | Port | URL |
|---------|------|-----|
| PostgreSQL | 5433 | `localhost:5433` |
| Redis | 6379 | `localhost:6379` |
| pgAdmin | 5050 | http://localhost:5050 |
| Prisma Studio | 5555 | http://localhost:5555 |
| Grafana | 3000 | http://localhost:3000 |
| Loki | 3100 | http://localhost:3100 |
| MeiliSearch | 7700 | http://localhost:7700 |
| Traefik | 80, 443, 8888 | http://localhost:8888 |

**Infrastructure Management**:
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

**See**: [Infrastructure Documentation](infrastructure/) for complete guide

---

## Quick Links

| I want to... | Go to... |
|--------------|----------|
| **Install AXIOM** | [Installation](getting-started/01-installation.md) |
| **Understand the architecture** | [Architecture Overview](getting-started/03-architecture-overview.md) |
| **Run tests** | [Testing Guide](developer-guide/08-testing.md) |
| **Deploy to production** | [Deployment](developer-guide/06-deployment.md) |
| **View logs** | [Logging Infrastructure](reference/logging-infrastructure.md) |
| **Contribute code** | [Code Guidelines](contributing/code-guidelines.md) |
| **See migration history** | [Migration Guide](MIGRATION-AXIOM.md) |

---

## Contributing

- [Code Guidelines](contributing/code-guidelines.md) - Standards and conventions
- [Git Workflow](contributing/git-workflow.md) - Branches, PRs, commits

---

**Platform Version:** 1.0.0
**Last Updated:** 2025-11-28 18:44
**Repository:** [github.com/seb155/AXIOM](https://github.com/seb155/AXIOM)
