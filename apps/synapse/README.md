<div align="center">

# AXOIQ SYNAPSE

### Model-Based Systems Engineering Platform for EPCM Automation

[![Version](https://img.shields.io/badge/version-0.2.4-blue.svg)](https://github.com/seb155/AXIOM/releases)
[![License](https://img.shields.io/badge/license-Proprietary-red.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-3776AB.svg?logo=python&logoColor=white)](https://python.org)
[![TypeScript](https://img.shields.io/badge/typescript-5.0+-3178C6.svg?logo=typescript&logoColor=white)](https://typescriptlang.org)
[![React](https://img.shields.io/badge/react-19-61DAFB.svg?logo=react&logoColor=black)](https://react.dev)
[![FastAPI](https://img.shields.io/badge/fastapi-0.121-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/postgresql-15-4169E1.svg?logo=postgresql&logoColor=white)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/docker-ready-2496ED.svg?logo=docker&logoColor=white)](https://docker.com)

<br/>

**Transform P&ID data into complete engineering deliverables**

*Reduce 320 hours of manual work to 20 hours per project (94% reduction)*

<br/>

[Getting Started](#-quick-start) •
[Features](#-key-features) •
[Documentation](#-documentation) •
[Architecture](#-architecture) •
[Roadmap](#-roadmap)

<br/>

---

</div>

## The Problem

Engineering teams spend **hundreds of hours** on repetitive tasks:

| Task | Manual Time | With SYNAPSE |
|------|-------------|--------------|
| Asset data completion | 80 hours | 4 hours |
| Cable schedule generation | 40 hours | 2 hours |
| IO allocation | 60 hours | 4 hours |
| Package deliverables | 80 hours | 6 hours |
| Quality checks | 60 hours | 4 hours |
| **Total** | **320 hours** | **20 hours** |

## The Solution

SYNAPSE automates engineering workflows through a **database-driven rule engine**:

```
Import 3,000 instruments → Rules auto-generate → 8,000+ complete assets
```

<br/>

## ✨ Key Features

<table>
<tr>
<td width="50%">

### 🔧 Rule-Based Automation

**7 Action Types:**
- `CREATE_CHILD` — Pump → Motor
- `CREATE_CABLE` — Auto-sized cables
- `SET_PROPERTY` — Apply standards
- `CREATE_PACKAGE` — Group deliverables
- `ALLOCATE_IO` — PLC terminal assignment
- `CREATE_RELATIONSHIP` — Asset linking
- `VALIDATE` — Compliance checks

**4-Tier Priority System:**
```
CLIENT (100) → Overrides all
PROJECT (50) → Project-specific
COUNTRY (30) → Electrical codes
FIRM (10)    → Company defaults
```

</td>
<td width="50%">

### 📊 Professional Deliverables

**Excel Template Export System (NEW v0.2.4):**
- ✅ IN-P040: Instrument Index
- ✅ CA-P040: Cable Schedule
- 📋 EL-P040: Electrical SLD (Planned)
- 📋 MC-P040: Motor Control (Planned)

**One-Click Export:**
- Excel with professional formatting
- Auto-sized columns & borders
- Project headers & footers
- Multi-sheet support ready
- [Quick Start Guide](./TEMPLATES-QUICKSTART.md)

**Compliance Built-In:**
- CEC-2021 (Canada)
- NEC-2023 (USA)
- IEC-60364 (International)

</td>
</tr>
<tr>
<td width="50%">

### 🌐 Graph-Based Data Model

**Unified Metamodel:**
- Equipment, Instruments, Cables
- Location hierarchies (FBS/LBS)
- Relationship tracking
- Visual graph editor

**Multi-Tenant:**
- Complete project isolation
- Client-level organization
- Role-based access

</td>
<td width="50%">

### 🖥️ Modern Interface

**Professional UI:**
- Resizable panels
- AG Grid data tables
- ReactFlow visualizations
- Dark/Light themes

**Developer Tools:**
- Real-time DevConsole
- Hierarchical audit logs
- Rule conflict detection
- Execution tracing

</td>
</tr>
</table>

<br/>

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                 │
│         React 19 • TypeScript • TailwindCSS • AG Grid           │
│                    Zustand • ReactFlow                           │
└────────────────────────────┬────────────────────────────────────┘
                             │ REST API
┌────────────────────────────▼────────────────────────────────────┐
│                         BACKEND                                  │
│              FastAPI • SQLAlchemy • Pydantic                    │
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ Rule Engine │  │  Ingestion  │  │  Validation │              │
│  │             │  │   Service   │  │   Service   │              │
│  │ • Loader    │  │             │  │             │              │
│  │ • Executor  │  │ • CSV/Excel │  │ • Conflicts │              │
│  │ • Enhanced  │  │ • Detection │  │ • Enforce   │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                       DATABASE                                   │
│                    PostgreSQL 15                                 │
│                                                                  │
│   metamodel_nodes • rule_definitions • action_logs • cables     │
└─────────────────────────────────────────────────────────────────┘
```

<br/>

## 🚀 Quick Start

### Prerequisites

- [Docker Desktop](https://docker.com/products/docker-desktop)
- [Node.js 18+](https://nodejs.org)
- [Python 3.11+](https://python.org)

### Option 1: Docker (Recommended)

```bash
# Clone repository
git clone https://github.com/seb155/EPCB-Tools.git
cd EPCB-Tools

# Optimize WSL/Docker (Windows only)
.\scripts\optimize_wsl.ps1
wsl --shutdown
# Restart Docker Desktop

# Start all services
docker-compose up -d

# Access application
# Frontend: http://localhost:4000
# Backend:  http://localhost:8001
# API Docs: http://localhost:8001/docs
```

### Option 2: Local Development

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
npm install
npm run dev  # http://localhost:4000
```

**Database:**
```bash
docker-compose up -d db  # PostgreSQL on port 5433
```

### Default Login

| Email | Password | Role |
|-------|----------|------|
| `admin@aurumax.com` | `admin123!` | Admin |

<br/>

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [Quick Start](./docs/0_AI_START.md) | 30-second setup guide |
| [Architecture](./docs/00_OVERVIEW/02_ARCHITECTURE.md) | System design |
| [Database Guide](./docs/00_OVERVIEW/07_DATABASE_GUIDE.md) | Schema reference |
| [Setup & Deploy](./docs/00_OVERVIEW/09_SETUP_DEPLOYMENT.md) | Installation guide |
| [Rules Guide](./docs/AI_NOTES/RULES_AND_WORKFLOWS_GUIDE.md) | Rule engine patterns |
| **[Templates & Export](./TEMPLATES-QUICKSTART.md)** | **Package export guide (NEW)** |
| **[Template System Docs](./backend/docs/templates-export-system.md)** | **Full technical docs (NEW)** |

### For AI Agents

| Resource | Purpose |
|----------|---------|
| [CLAUDE.md](./CLAUDE.md) | AI assistant instructions |
| [.agent/rules/](./.agent/rules/) | 20 behavior rules |
| [.agent/workflows/](./.agent/workflows/) | Automated workflows |

<br/>

## 🛠️ Tech Stack

<table>
<tr>
<td align="center" width="20%">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/react/react-original.svg" width="40" height="40"/><br/>
<b>React 19</b><br/>
<sub>UI Framework</sub>
</td>
<td align="center" width="20%">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/typescript/typescript-original.svg" width="40" height="40"/><br/>
<b>TypeScript</b><br/>
<sub>Type Safety</sub>
</td>
<td align="center" width="20%">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" width="40" height="40"/><br/>
<b>Python 3.11</b><br/>
<sub>Backend</sub>
</td>
<td align="center" width="20%">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/fastapi/fastapi-original.svg" width="40" height="40"/><br/>
<b>FastAPI</b><br/>
<sub>REST API</sub>
</td>
<td align="center" width="20%">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/postgresql/postgresql-original.svg" width="40" height="40"/><br/>
<b>PostgreSQL</b><br/>
<sub>Database</sub>
</td>
</tr>
<tr>
<td align="center">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/docker/docker-original.svg" width="40" height="40"/><br/>
<b>Docker</b><br/>
<sub>Containers</sub>
</td>
<td align="center">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/tailwindcss/tailwindcss-original.svg" width="40" height="40"/><br/>
<b>TailwindCSS</b><br/>
<sub>Styling</sub>
</td>
<td align="center">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/sqlalchemy/sqlalchemy-original.svg" width="40" height="40"/><br/>
<b>SQLAlchemy</b><br/>
<sub>ORM</sub>
</td>
<td align="center">
<img src="https://www.ag-grid.com/images/ag-logos/svg-logos/AG-Grid-Logo.svg" width="40" height="40"/><br/>
<b>AG Grid</b><br/>
<sub>Data Tables</sub>
</td>
<td align="center">
<img src="https://reactflow.dev/img/logo.svg" width="40" height="40"/><br/>
<b>ReactFlow</b><br/>
<sub>Graphs</sub>
</td>
</tr>
</table>

<br/>

## 📈 Roadmap

### Current: v0.2.0

| Phase | Status | Description |
|-------|--------|-------------|
| 1. Multi-Project | ✅ Complete | Client/project isolation |
| 2. Rule Engine | ✅ Complete | 7 action types, 4-tier priority |
| 3. Cables | ✅ Complete | Auto-generation with sizing |
| 4. Ingestion | ✅ Complete | CSV/Excel import with detection |
| 5. DevConsole | ✅ Complete | Hierarchical audit logs |

### Planned: v0.3.0+

| Feature | Status | Description |
|---------|--------|-------------|
| AI Assistant | 📋 Planned | Natural language queries |
| P&ID OCR | 📋 Planned | Drawing data extraction |
| DWG Generation | 📋 Planned | Auto-generate drawings |
| Azure AD | 📋 Planned | Enterprise SSO |
| 3D Visualization | 📋 Planned | Spatial asset view |

<br/>

## 💼 Business Value

<table>
<tr>
<td align="center" width="25%">
<h3>⏱️ 94%</h3>
<b>Time Reduction</b><br/>
<sub>320h → 20h per project</sub>
</td>
<td align="center" width="25%">
<h3>💰 $50K+</h3>
<b>Cost Savings</b><br/>
<sub>Per major project</sub>
</td>
<td align="center" width="25%">
<h3>📉 90%</h3>
<b>Fewer Errors</b><br/>
<sub>Automated validation</sub>
</td>
<td align="center" width="25%">
<h3>📊 100%</h3>
<b>Traceability</b><br/>
<sub>Complete audit trail</sub>
</td>
</tr>
</table>

<br/>

## 🤝 Contributing

1. Read the [Guidelines](./docs/00_OVERVIEW/03_GUIDELINES.md)
2. Check [CLAUDE.md](./CLAUDE.md) for AI collaboration
3. Create a feature branch
4. Follow existing patterns
5. Write tests (>80% coverage)
6. Submit a pull request

<br/>

## 📄 License

**AXOIQ SYNAPSE** — Proprietary Software

Copyright © 2024-2025 AXOIQ. All rights reserved.

<br/>

---

<div align="center">

**Built with ❤️ for EPCM Engineers**

[Report Bug](https://github.com/seb155/EPCB-Tools/issues) •
[Request Feature](https://github.com/seb155/EPCB-Tools/issues) •
[Documentation](./docs/0_AI_START.md)

</div>
