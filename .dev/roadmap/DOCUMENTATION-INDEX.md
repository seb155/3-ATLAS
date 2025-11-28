# SYNAPSE Roadmap & Documentation Index

**Complete reference for AI agents and developers**

---

## 🗺️ Roadmap Overview

**Current Version:** v0.2.1 (Logging & Monitoring)  
**Next Version:** v0.2.2 (UX Professional)  
**Target v1.0.0:** August 2026

[**→ Full Roadmap**](.dev/roadmap/README.md)

---

## 📋 Core Platform (v0.2.x)

### v0.2.1 - Logging & Monitoring ✅ DONE
- Loki + Grafana + Promtail
- WebSocket real-time logging
- DevConsole V3 (In Development)

### v0.2.2 - UX Professional (Next)
[**→ Sprint Details**](.dev/roadmap/current-sprint.md)
- Clickable navigation
- Context menus
- Command palette (Ctrl+K)
- Keyboard shortcuts

### v0.2.3-v0.2.11 - Core Features
[**→ Detailed Specs**](.dev/roadmap/backlog/core-platform-v0.2.x.md)

---

## 📚 Feature Documentation (Backlog)

### 3-Tier Asset Model (v0.2.3)
[**→ Technical Specs**](.dev/roadmap/backlog/3-tier-asset-model.md)  
[**→ User Guide**](docs/reference/asset-lifecycle.md)

- Engineering Assets (design)
- Catalog Assets (procurement)
- Physical Assets (as-built)

### Breakdown Structures (v0.2.4)
[**→ Technical Specs**](.dev/roadmap/backlog/breakdown-structures.md)  
[**→ User Guide**](docs/reference/breakdown-structures-guide.md)

- FBS (Functional), LBS (Location), WBS (Work)
- OBS (Organization), CBS (Cost), PBS (Product)

### Package Generation (v0.2.6)
[**→ Technical Specs**](.dev/roadmap/backlog/package-generation.md)

- Excel (openpyxl) + PDF (WeasyPrint)
- Templates: IN-P040, EL-M040, CA-P040, IO-P040

### Dev Environment & Owner Portal (v0.1.x)
[**→ Technical Specs**](.dev/roadmap/backlog/dev-environment-owner-portal.md)
[**→ Developer Guide**](docs/developer-guide/owner-portal-and-analytics.md)

### PLC & Panel Planning (v0.2.6+)
[**→ Technical Specs**](.dev/roadmap/backlog/control-architecture-planning.md)

- PLC systems per area
- Panels (PCP/RIO) and IO modules
- IO channel allocation for IO-P040

### Search & Navigation (v0.2.5)
[**→ Technical Specs**](.dev/roadmap/backlog/search-navigation.md)

- MeiliSearch (self-hosted, 10K+ assets)
- Full-text search, typo-tolerant
- Faceted filters

### Change Management (v0.2.7-v0.2.8)
[**→ Technical Specs**](.dev/roadmap/backlog/change-management.md)  
[**→ User Guide**](docs/workflows/creating-baselines.md)

- Version history per asset
- Baselines (project snapshots)
- Impact analysis
- Change request tracking

### Rule Visualization & Editor (v0.2.9-v0.2.11)
[**→ Technical Specs**](.dev/roadmap/backlog/rule-visualization-editor.md)  
[**→ Rule Templates**](docs/reference/rule-templates.md)

- 2D rule graph (ReactFlow)
- Visual editor (Natural Language, Form, Node-Based, Code)
- 15 predefined templates

### Background Processing (v0.4.0)
[**→ Technical Specs**](.dev/roadmap/backlog/background-processing.md)

- Celery + Redis
- Async imports (1K-5K rows)
- Scheduled jobs

---

## 🎯 Future Versions

### v0.3.0 - Multi-Tenant Auth
[**→ Technical Specs**](.dev/roadmap/backlog/multi-tenant-auth.md)  
[**→ Next Sprint**](.dev/roadmap/next-sprint.md)

- Azure AD + SSO
- RBAC (5 roles)
- Organization hierarchy

### v0.5.0 - AI Integration
[**→ Technical Specs**](.dev/roadmap/backlog/ai-strategy.md)

- Ollama + LLaMA 70B (local)
- Navigation chatbot
- Rule explanation

### v0.6.0 - P&ID Intelligence
[**→ Technical Specs**](.dev/roadmap/backlog/pid-electrical-strategy.md)

- Claude Vision API
- Symbol recognition
- Auto-create assets

### v0.7.0 - Drawing Generation
[**→ Technical Specs**](.dev/roadmap/backlog/pid-electrical-strategy.md)

- SVG/PDF P&ID generation
- DXF export (ezdxf)

### v1.0.0 - Production Ready
- Full test coverage
- Security audit
- Documentation complete

---

## 📖 User Documentation

### Getting Started
- [Installation](docs/getting-started/01-installation.md)
- [First Steps](docs/getting-started/02-first-steps.md)
- [Architecture Overview](docs/getting-started/03-architecture-overview.md)

### Developer Guides
- [Project Structure](docs/developer-guide/01-project-structure.md)
- [Backend Guide](docs/developer-guide/02-backend-guide.md)
- [Frontend Guide](docs/developer-guide/03-frontend-guide.md)
 - [Database](docs/developer-guide/04-database.md)
 - [Testing](docs/developer-guide/05-testing.md)
 - [Deployment](docs/developer-guide/06-deployment.md)
 - [Workflow Engine](docs/developer-guide/workflow-engine.md) ✨ NEW
 - [Owner Analytics & Portal](docs/developer-guide/owner-portal-and-analytics.md)
 - [Owner Portal React App](docs/developer-guide/owner-portal-react.md)

### Reference
- [API Endpoints](docs/reference/api-endpoints.md)
- [Database Schema](docs/reference/database-schema.md)
- [Rule Engine](docs/reference/rule-engine.md)
- [Logging Infrastructure](docs/reference/logging-infrastructure.md)
- [DevConsole V3](docs/reference/devconsole-v3.md) ✨ NEW
- [Asset Lifecycle](docs/reference/asset-lifecycle.md)
- [Breakdown Structures Guide](docs/reference/breakdown-structures-guide.md)
- [Rule Templates](docs/reference/rule-templates.md)
- [Tech Stack](docs/reference/tech-stack.md)

### Workflows
- [Creating Baselines](docs/workflows/creating-baselines.md)
- [Using DevConsole](docs/workflows/using-devconsole.md) ✨ NEW

---

## 🔧 Development Context

### Current State
[**→ Project State**](.dev/context/project-state.md)

- Version: v0.2.1
- Next: v0.2.2 (UX Professional)
- Last updated: 2025-11-24

### Daily Tracking
[**→ Today's Journal**](.dev/journal/2025-11/2025-11-24.md)

### Credentials & Access
[**→ Credentials**](.dev/context/credentials.md)

- App: http://localhost:4000
- API: http://localhost:8001/docs
- Grafana: http://localhost:3000
- pgAdmin: http://localhost:5050

### Shared Context
[**→ Shared Context**](.dev/context/shared-context.md)

- Project structure
- Tech stack
- User preferences

### Code Quality & Reviews
- [Code Quality Validation Rules](.dev/context/code-quality-rules.md)
- [Code & Architecture Review Program](.dev/context/code-review-program.md)

---

## 🎨 Design Patterns

### Database
- PostgreSQL only (no SQLite)
- Alembic migrations
- SQLAlchemy ORM

### Backend
- FastAPI
- Pydantic validation
- Service layer pattern

### Frontend
- React 19
- TypeScript
- Zustand (state)
- TanStack Query (data)

### Infrastructure
- Docker + Docker Compose
- Workspace (shared) + Apps (specific)
- Loki/Grafana logging

---

## 🚀 Quick Start for AI Agents

### Planning New Work
1. Read [project-state.md](.dev/context/project-state.md)
2. Check [current-sprint.md](.dev/roadmap/current-sprint.md)
3. Review relevant backlog file in `.dev/roadmap/backlog/`

### Implementing Features
1. Follow specs in backlog file
2. Check [shared-context.md](.dev/context/shared-context.md) for patterns
3. Refer to developer guides in `docs/developer-guide/`

### Testing & Verification
1. Follow verification plan in backlog file
2. Check [testing guide](docs/developer-guide/05-testing.md)

### Documentation
1. Update [project-state.md](.dev/context/project-state.md)
2. Add entry to [journal](.dev/journal/2025-11/2025-11-24.md)
3. Update sprint files if needed

---

## 📊 Documentation Coverage

### Roadmap (100%)
- ✅ Main roadmap (v0.2.x → v1.0.0)
- ✅ Current sprint (v0.2.2)
- ✅ Next sprint (v0.3.0)
- ✅ All backlog files (8)

### User Guides (60%)
- ✅ Asset Lifecycle
- ✅ Breakdown Structures
- ✅ Rule Templates
- ✅ Creating Baselines
- ⏳ Package generation (optional)
- ⏳ Impact analysis (optional)
- ⏳ Version history (optional)

### Technical Docs (80%)
- ✅ Logging infrastructure
- ✅ All backlog specifications
- ⏳ Some API references (partial)

---

**For AI Agents:** This index provides complete navigation to all roadmap and documentation resources. Start with project-state.md, then dive into specific backlog files as needed.

---

**Version:** 1.0  
**Last Updated:** 2025-11-24
