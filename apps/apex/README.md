# APEX - Enterprise Portal

> **A**pplication **P**ortal & **EX**ecutive Dashboard

APEX is the enterprise portal and dashboard for the AXIOM platform. It serves as the central launcher and health monitoring hub for all business applications.

## Status

**Phase:** Planning
**Target:** Q2 2026

## Overview

APEX provides:
- App launcher for SYNAPSE and future business apps
- Health monitoring and metrics visualization
- Executive-level dashboards
- System status overview

```
┌────────────────────────────────────────────────────────┐
│                    APEX (Portal)                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │   SYNAPSE   │  │  App Future │  │  App Future │   │
│  │   Launch    │  │   Launch    │  │   Launch    │   │
│  └─────────────┘  └─────────────┘  └─────────────┘   │
│                                                        │
│  ┌────────────────────────────────────────────────┐   │
│  │              Health Dashboard                   │   │
│  │  Services │ Metrics │ Alerts │ Status          │   │
│  └────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────┘
```

## Relationship with ATLAS

APEX is an **application** that runs on top of ATLAS (AI OS). It uses:
- CORTEX for AI-powered insights
- ATLAS agents for automation
- FORGE for infrastructure

## Planned Features

- App launcher with status indicators
- Real-time health monitoring
- Executive metrics dashboard
- Integration with Grafana/monitoring
- Role-based access (owner view vs admin view)

## Stack (Planned)

- React 19 + TypeScript
- TailwindCSS
- React Query + React Router
- Axios (API client)

## Port

| Service | Port |
|:---|:---:|
| APEX Frontend | 6000 |

## Files (Current)

The current code was originally "Owner Portal" (PRISM) - a read-only dashboard showing health, tests, tech debt, and architecture from `synapse_analytics.owner.*`.

### Development

```bash
cd apps/apex
npm install
npm run dev    # http://localhost:6000
```

### Build

```bash
npm run build
npm run preview
```

## Integration with AXIOM

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

---

*Part of the AXIOM Platform by AXoiq*
