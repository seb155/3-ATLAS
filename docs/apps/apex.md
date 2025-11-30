# APEX - Enterprise Portal

> **A**pplication **P**ortal & **EX**ecutive Dashboard

## Overview

APEX is the enterprise portal of AXIOM, providing a unified dashboard for application launching, health monitoring, and executive-level insights.

**Note:** APEX was formerly known as PRISM. The name was changed to better reflect its role as the application portal.

## Key Features

### App Launcher
- Launch SYNAPSE and future business apps
- Status indicators for each app
- Quick access to app settings

### Health Dashboard
- Real-time service health
- Key metrics and KPIs
- System alerts
- Activity feed

### Executive View
- Project metrics overview
- Resource allocation
- Timeline views
- Custom reports

### Integration Hub
- Links to SYNAPSE projects
- NEXUS knowledge access
- CORTEX AI insights (via ATLAS)
- Unified search

---

## Relationship with ATLAS

APEX is an **application** that runs on top of ATLAS (AI OS):

```
         ATLAS (AI OS)
              │
              ▼
┌─────────────────────────────────┐
│            APEX                 │
│     (Enterprise Portal)         │
│              │                  │
│   ┌──────────┴──────────┐      │
│   │                     │      │
│   ▼                     ▼      │
│ SYNAPSE              Future    │
│ (Launch)             Apps      │
└─────────────────────────────────┘
```

- Uses CORTEX (within ATLAS) for AI-powered insights
- Uses ATLAS agents for automation
- Uses FORGE for infrastructure

---

## Architecture

```
apps/apex/
├── src/
│   ├── components/
│   ├── pages/
│   ├── hooks/
│   ├── services/
│   └── shared/
│       ├── api/
│       └── config/
├── package.json
└── vite.config.ts
```

---

## Quick Start

```powershell
# From AXIOM root
cd apps/apex

# Install dependencies
npm install

# Start dev server
npm run dev
```

**Access:** http://localhost:6000

---

## Status

**Current Status:** Planning

APEX is in early planning phase. The codebase contains the original "Owner Portal" functionality.

### Roadmap
- [ ] App launcher with status indicators
- [ ] Real-time health monitoring
- [ ] Executive metrics dashboard
- [ ] Integration with Grafana/monitoring
- [ ] Role-based access

---

## Port Allocation

| Service | Port |
|---------|------|
| APEX Frontend | 6000 |

*In APEX range (6000-6999)*

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 19, TypeScript, TailwindCSS |
| State | React Query |
| Routing | React Router |
| Charts | Recharts, D3.js (planned) |

---

## Related Documentation

- [ATLAS](./atlas.md) - AI OS (parent system)
- [SYNAPSE](./synapse.md) - Engineering app
- [NEXUS](./nexus.md) - Knowledge portal
- [Architecture Overview](../getting-started/03-architecture-overview.md)
