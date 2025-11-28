<div align="center">

# AXIOM

### **The Unified Engineering & Knowledge Platform**

*Streamline your engineering workflows, centralize knowledge, and collaborate with AI*

[![Platform](https://img.shields.io/badge/Platform-AXIOM-blue?style=for-the-badge)](https://github.com/seb155/AXIOM)
[![Version](https://img.shields.io/badge/Version-1.0.0-green?style=for-the-badge)](./CHANGELOG.md)
[![License](https://img.shields.io/badge/License-Proprietary-red?style=for-the-badge)](#license)

[**Get Started**](#-quick-start) · [**Applications**](#-applications) · [**Documentation**](#-documentation) · [**Tech Stack**](#-technology-stack)

---

</div>

## What is AXIOM?

**AXIOM** is an integrated enterprise platform that brings together engineering automation, knowledge management, and AI-powered development into a single, cohesive ecosystem.

### The Problem

- Engineering data scattered across Excel files, emails, and disconnected tools
- Knowledge trapped in silos - notes here, tasks there, documentation elsewhere
- Manual processes eating up valuable engineering time
- No traceability or audit trail for critical decisions

### The Solution

AXIOM provides **four integrated applications** that work together seamlessly:

<div align="center">

| | Application | What it does | Who it's for |
|:---:|:---|:---|:---|
| ⚡ | [**SYNAPSE**](#-synapse---engineering-automation) | Automates engineering workflows & generates deliverables | Engineers, Project Managers |
| 🔮 | [**NEXUS**](#-nexus---knowledge-hub) | Centralizes notes, wiki, tasks with visual knowledge graphs | Everyone |
| 💎 | [**PRISM**](#-prism---enterprise-dashboard) | Project dashboards, metrics, and team oversight | Managers, Stakeholders |
| 🤖 | [**ATLAS**](#-atlas---ai-collaboration) | AI-assisted development and decision support | Developers, Engineers |

</div>

---

## 🚀 Applications

### ⚡ SYNAPSE - Engineering Automation

> **Model-Based Systems Engineering (MBSE) for EPCM Projects**

Transform your engineering data into actionable deliverables automatically.

**Key Features:**
- 📥 **Smart Import** - CSV/Excel data ingestion with validation
- 🔧 **Rule Engine** - Automated cable sizing, equipment creation, package generation
- 📊 **Visual Metamodel** - Graph-based asset relationships
- 📦 **Package Export** - Generate Excel/PDF deliverables from templates
- 📜 **Full Traceability** - Complete audit trail of every action

**Use Case:** Import a BBA list → Rules auto-create cables, instruments, packages → Export ready-to-use deliverables

```
Status: MVP Development (Target: December 2025)
```

<details>
<summary>📸 Screenshots (coming soon)</summary>

*Interface screenshots will be added here*

</details>

---

### 🔮 NEXUS - Knowledge Hub

> **Your Second Brain - Notes, Wiki, Tasks, and Knowledge Graphs**

Stop losing information. Connect your thoughts visually.

**Key Features:**
- 📝 **Rich Notes** - Markdown with live preview
- 📚 **Team Wiki** - Collaborative documentation
- ✅ **Task Management** - Kanban boards and lists
- 🌐 **3D Knowledge Graph** - Visualize connections between ideas
- 🎨 **13 Themes** - From Tokyo Night to Catppuccin

**Use Case:** Take meeting notes → Link to project wiki → See connections in graph → Never lose context

```
Status: Phase 1.5 (Visual Polish Complete)
```

---

### 💎 PRISM - Enterprise Dashboard

> **See Everything. Decide Faster.**

One dashboard for all your projects and teams.

**Key Features:**
- 📈 **Project Metrics** - Real-time health indicators
- 👥 **Team Overview** - Workload and capacity
- 🏗️ **Infrastructure Status** - Service health monitoring
- 📋 **Technical Debt** - Track and prioritize improvements

```
Status: In Development
```

---

### 🤖 ATLAS - AI Collaboration

> **Your AI Engineering Partner**

Leverage AI to accelerate development and decision-making.

**Key Features:**

- 🧠 **15 Specialized AI Agents** - Each expert in their domain
- 🔄 **Hierarchical Workflows** - ATLAS orchestrates, agents execute
- 🔗 **Context-Aware** - Remembers your preferences and project state
- 💬 **Natural Interaction** - Talk naturally or use slash commands

**Quick Example:**

```
You: "Add a refresh button to the project list"
ATLAS: "Simple frontend task. Dispatching to FRONTEND-BUILDER..."
→ Code created, tested, ready to commit
```

```
Status: Active (AI Agents System Complete)
```

See [AI Agents Guide](./docs/developer-guide/ai-agents-overview.md) for details.

---

## 🏗️ Architecture

<div align="center">

```
┌─────────────────────────────────────────────────────────────────┐
│                        AXIOM PLATFORM                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│   │ SYNAPSE  │  │  NEXUS   │  │  PRISM   │  │  ATLAS   │       │
│   │   ⚡     │  │    🔮    │  │    💎    │  │    🤖    │       │
│   │ :4000    │  │  :5173   │  │  :5174   │  │  :5175   │       │
│   └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
│        │             │             │             │              │
│        └─────────────┴─────────────┴─────────────┘              │
│                            │                                     │
│   ┌────────────────────────┴────────────────────────┐           │
│   │                  FORGE Infrastructure           │           │
│   │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌───────┐ │           │
│   │  │PostgreSQL│ │  Redis  │ │ Grafana │ │ Loki  │ │           │
│   │  │  :5433  │ │  :6379  │ │  :3000  │ │ :3100 │ │           │
│   │  └─────────┘ └─────────┘ └─────────┘ └───────┘ │           │
│   └─────────────────────────────────────────────────┘           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

</div>

### Project Structure

```
AXIOM/
├── 📁 apps/
│   ├── 📁 synapse/           # ⚡ MBSE Platform
│   │   ├── backend/          #    FastAPI + SQLAlchemy
│   │   └── frontend/         #    React 19 + Vite
│   ├── 📁 nexus/             # 🔮 Knowledge Graph
│   ├── 📁 prism/             # 💎 Enterprise Portal
│   └── 📁 atlas/             # 🤖 AI Collaboration
│
├── 📁 forge/                 # 🔧 Shared Infrastructure
│   ├── docker-compose.yml    #    All services
│   ├── config/               #    Service configurations
│   └── databases/            #    Data persistence
│
├── 📁 docs/                  # 📚 Documentation
├── 📁 .agent/                # 🤖 AI Development Workflows
└── 📁 .dev/                  # 📋 Development Context
```

---

## 💻 Technology Stack

<div align="center">

### Backend

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.121+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=flat-square&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?style=flat-square&logo=redis&logoColor=white)](https://redis.io)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-D71F00?style=flat-square)](https://sqlalchemy.org)

### Frontend

[![React](https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6?style=flat-square&logo=typescript&logoColor=white)](https://typescriptlang.org)
[![Vite](https://img.shields.io/badge/Vite-7.2+-646CFF?style=flat-square&logo=vite&logoColor=white)](https://vitejs.dev)
[![TailwindCSS](https://img.shields.io/badge/Tailwind-4+-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white)](https://tailwindcss.com)
[![Zustand](https://img.shields.io/badge/Zustand-5+-000000?style=flat-square)](https://zustand-demo.pmnd.rs)

### Infrastructure

[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white)](https://docker.com)
[![Traefik](https://img.shields.io/badge/Traefik-3.x-24A1C1?style=flat-square&logo=traefik&logoColor=white)](https://traefik.io)
[![Grafana](https://img.shields.io/badge/Grafana-11-F46800?style=flat-square&logo=grafana&logoColor=white)](https://grafana.com)

</div>

---

## 🚀 Quick Start

### Prerequisites

- [Docker Desktop](https://docker.com/products/docker-desktop) (required)
- [Node.js 20+](https://nodejs.org) (for frontend development)
- [Python 3.11+](https://python.org) (for backend development)
- PowerShell (Windows) or Bash (Linux/Mac)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/seb155/AXIOM.git
cd AXIOM

# 2. Start the platform
.\dev.ps1          # Windows
# ./dev.sh         # Linux/Mac (coming soon)
```

### Access Your Applications

| Application | URL | Description |
|:---:|:---|:---|
| ⚡ SYNAPSE | [localhost:4000](http://localhost:4000) | Engineering Platform |
| 🔮 NEXUS | [localhost:5173](http://localhost:5173) | Knowledge Hub |
| 📊 Grafana | [localhost:3000](http://localhost:3000) | Monitoring Dashboard |
| 🗄️ pgAdmin | [localhost:5050](http://localhost:5050) | Database Admin |
| 🔍 Prisma | [localhost:5555](http://localhost:5555) | Schema Browser |

**Default Login:** `admin@axoiq.com` / `admin123!`

---

## 🔧 FORGE Infrastructure

All applications share a common infrastructure layer called **FORGE**:

| Service | Purpose | Port |
|:---|:---|:---:|
| **PostgreSQL** | Primary database for all apps | 5433 |
| **Redis** | Caching, sessions, queues | 6379 |
| **Grafana** | Metrics & log visualization | 3000 |
| **Loki** | Log aggregation | 3100 |
| **MeiliSearch** | Full-text search engine | 7700 |
| **Prisma Studio** | Database schema browser | 5555 |
| **pgAdmin** | PostgreSQL admin interface | 5050 |

```powershell
# Start only infrastructure
cd forge
docker-compose up -d forge-postgres forge-redis

# Start all FORGE services
docker-compose up -d
```

---

## 🤖 AI Agents System

AXIOM includes a **complete AI development assistant** with 15 specialized agents:

<div align="center">

| Layer | Agents | AI Model | Role |
|:---:|:---|:---:|:---|
| 🎯 | **ATLAS**, BRAINSTORM, SYSTEM-ARCHITECT | Opus | Orchestration & Strategy |
| 📋 | **PLANNER**, DEBUGGER, UX-DESIGNER | Sonnet | Analysis & Planning |
| 🔨 | **BACKEND**, FRONTEND, ARCHITECT, INTEGRATION | Sonnet/Opus | Code Implementation |
| ✅ | **QA-TESTER**, ISSUE-REPORTER | Haiku | Validation |
| 📊 | **DEV-TRACKER**, GIT-MANAGER, DOC-WRITER | Haiku | Tracking & Docs |

</div>

### Quick Commands

```bash
/new-session          # Start a new dev session
/implement [feature]  # Implement a feature
/debug [error]        # Debug an error
/test                 # Run tests
/commit               # Create a clean commit
/brainstorm [idea]    # Creative session
```

📖 **Full Guide:** [AI Agents Overview](./docs/developer-guide/ai-agents-overview.md) | [Technical Details](./docs/developer-guide/ai-agents-system.md)

---

## 📚 Documentation

| Document | Description |
|:---|:---|
| 📖 [**CLAUDE.md**](./CLAUDE.md) | AI assistant development guide |
| 🤖 [**AI Agents Guide**](./docs/developer-guide/ai-agents-overview.md) | How to use the AI agents system |
| 📋 [**CHANGELOG.md**](./CHANGELOG.md) | Version history and releases |
| 🔄 [**Migration Guide**](./docs/MIGRATION-AXIOM.md) | Platform migration documentation |
| 📊 [**Project State**](./.dev/context/project-state.md) | Current development status |

### Application Documentation

| App | Docs |
|:---|:---|
| ⚡ SYNAPSE | [README](./apps/synapse/README.md) · [CHANGELOG](./apps/synapse/CHANGELOG.md) · [Deployment](./apps/synapse/DEPLOYMENT.md) |
| 🔮 NEXUS | [README](./apps/nexus/README.md) · [CLAUDE](./apps/nexus/CLAUDE.md) · [Architecture](./apps/nexus/docs/ARCHITECTURE.md) |
| 💎 PRISM | [README](./apps/prism/README.md) |
| 🤖 ATLAS | [README](./apps/atlas/README.md) |

---

## 🧪 Development

### Running Tests

```bash
# Backend (SYNAPSE)
cd apps/synapse/backend
pytest --cov=app --cov-report=html

# Frontend (SYNAPSE)
cd apps/synapse/frontend
npm run test
npm run test:coverage
```

### Code Quality

```bash
# Backend linting
ruff check . --fix
black .

# Frontend linting
npm run lint:fix
npm run type-check
```

### Docker Commands

```bash
# View logs
docker logs synapse-backend -f --tail 100

# Restart a service
docker restart synapse-backend

# Access database
docker exec -it forge-postgres psql -U postgres -d synapse
```

---

## 🗺️ Roadmap

### Current Focus (Q4 2025)
- [ ] SYNAPSE MVP - Demo-ready by December 20, 2025
- [ ] CSV Import → Rule Engine → Package Export pipeline
- [ ] Full traceability and audit logging

### Next Up (Q1 2026)
- [ ] NEXUS Phase 2 - Backend integration
- [ ] PRISM initial release
- [ ] ATLAS planning and prototyping

### Future
- [ ] Multi-tenant support
- [ ] Advanced AI integrations
- [ ] Mobile companion app

---

## 🤝 Contributing

This is currently a private project. For access or collaboration inquiries, please contact the repository owner.

---

## 📄 License

**Proprietary** - All rights reserved.

This software and its documentation are proprietary and confidential. Unauthorized copying, distribution, or use is strictly prohibited.

---

<div align="center">

### Built with ❤️ by **AXoiq**

*Engineering the future, one platform at a time*

[![GitHub](https://img.shields.io/badge/GitHub-seb155-181717?style=flat-square&logo=github)](https://github.com/seb155)

</div>
