# SYNAPSE Documentation

> **Model-Based Systems Engineering Platform for EPCM Automation**

Welcome to SYNAPSE! This documentation will help you get started, develop features, and contribute.

---

## 🚀 Getting Started (5 minutes)

**New to SYNAPSE?** Start here:

1. **[Installation](getting-started/01-installation.md)** - Setup in 5 minutes with `.\dev.ps1`
2. **[First Steps](getting-started/02-first-steps.md)** - Login, navigate, import data
3. **[Architecture Overview](getting-started/03-architecture-overview.md)** - Understand the system

---

## 🔧 Developer Guide

**Building features?** Deep dive here:

- **[Project Structure](developer-guide/01-project-structure.md)** - Monorepo, workspace/apps
- **[Backend Guide](developer-guide/02-backend-guide.md)** - FastAPI services & modules
- **[Frontend Guide](developer-guide/03-frontend-guide.md)** - React apps (SYNAPSE + Owner Portal)
- **[Database](developer-guide/04-database.md)** - Postgres layout & schemas
- **[Testing](developer-guide/08-testing.md)** - pytest, Playwright, Vitest UI
- **[Deployment](developer-guide/06-deployment.md)** - DEV vs PROD, Docker, Proxmox

---

## 📚 Reference

**Looking something up?**

- **[API Endpoints](reference/api-endpoints.md)** - REST API reference
- **[Database Schema](reference/database-schema.md)** - Tables, relationships
- **[Rule Engine](reference/rule-engine.md)** - Rules deep dive
- **[Logging Infrastructure](reference/logging-infrastructure.md)** - Loki, Grafana, WebSocket
- **[Tech Stack](reference/tech-stack.md)** - Technologies used

**Roadmap & Planning:**

- **[Roadmap Overview](../.dev/roadmap/README.md)** - v0.2.x → v1.0.0 complete roadmap
- **[3-Tier Asset Model](../.dev/roadmap/backlog/3-tier-asset-model.md)** - Engineering/Catalog/Physical
- **[Breakdown Structures](../.dev/roadmap/backlog/breakdown-structures.md)** - FBS/LBS/WBS/CBS/PBS/OBS
- **[Package Generation](../.dev/roadmap/backlog/package-generation.md)** - Excel/PDF deliverables
- **[Search & Navigation](../.dev/roadmap/backlog/search-navigation.md)** - MeiliSearch integration
- **[Change Management](../.dev/roadmap/backlog/change-management.md)** - Impact analysis, versioning, baselines
- **[Rule Visualization & Editor](../.dev/roadmap/backlog/rule-visualization-editor.md)** - Visual rule management
- **[Background Processing](../.dev/roadmap/backlog/background-processing.md)** - Celery + Redis

---

## 🤝 Contributing

**Want to contribute?**

- **[Code Guidelines](contributing/code-guidelines.md)** - Standards, conventions
- **[Git Workflow](contributing/git-workflow.md)** - Branches, PRs, commits
- **[AI Collaboration](contributing/ai-collaboration.md)** - Working with AI agents

---

## 📦 Archive

Old documentation structure is preserved in [`archive/`](archive/) for reference.

---

## Quick Links

| I want to... | Go to... |
|--------------|----------|
| **Install SYNAPSE** | [Installation](getting-started/01-installation.md) |
| **Add a backend endpoint** | [Backend Guide](developer-guide/02-backend-guide.md) |
| **Add a UI component** | [Frontend Guide](developer-guide/03-frontend-guide.md) |
| **Understand the database** | [Database](developer-guide/04-database.md) |
| **Run tests** | [Testing Guide](developer-guide/08-testing.md) |
| **Deploy to production** | [Deployment](developer-guide/06-deployment.md) |
| **See API docs** | [API Reference](reference/api-endpoints.md) |
| **View logs** | [Logging Infrastructure](reference/logging-infrastructure.md) |
| **Contribute code** | [Code Guidelines](contributing/code-guidelines.md) |

---

**Version:** 1.1
**Last Updated:** 2025-11-26
