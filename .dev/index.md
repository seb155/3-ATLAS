# Project Context Index (CAG)

> **Context-Aware Generation Index**
> Use this file to find the right documentation for your task.

---

## Quick Load (Session Start)

**Always read these first:**

| File | Purpose | Tokens |
|------|---------|--------|
| `ATLAS.md` | Master index, AI rules | ~800 |
| `.dev/context/project-state.md` | Current project status | ~500 |
| `.dev/context/current-sprint.md` | Active sprint goals | ~300 |

**Total session start:** ~1,600 tokens (minimal footprint)

---

## On-Demand Loading

### Working on Backend?
```
Load: .dev/patterns/backend/
```
| Pattern | File | When to use |
|---------|------|-------------|
| FastAPI Endpoint | `fastapi-endpoint.md` | Creating new API route |
| Multi-Tenancy | `multi-tenancy.md` | Project-scoped queries |
| Alembic Migration | `alembic-migration.md` | Database changes |
| Pydantic Schemas | `pydantic-schemas.md` | Request/response models |

### Working on Frontend?
```
Load: .dev/patterns/frontend/
```
| Pattern | File | When to use |
|---------|------|-------------|
| React Component | `react-component.md` | New UI component |
| Zustand Store | `zustand-store.md` | State management |
| Shadcn/UI | `shadcn-ui.md` | UI components |
| API Integration | `api-client.md` | Backend calls |

### Working on DevOps?
```
Load: .dev/patterns/devops/
```
| Pattern | File | When to use |
|---------|------|-------------|
| Docker Service | `docker-service.md` | New container |
| CI/CD | `ci-cd.md` | GitHub Actions |
| Deployment | `deployment.md` | Production deploy |

---

## Project-Specific Context

### SYNAPSE (Primary Project)
| Need | File |
|------|------|
| Architecture | `docs/architecture/` |
| API Conventions | `.dev/project/api-conventions.md` |
| UI Patterns | `.dev/project/ui-patterns.md` |
| Version Plan | `.dev/project/version-plan.md` |
| Tech Stack | `.dev/context/tech-stack.md` |
| Credentials | `.dev/context/credentials.md` |

### Dev Hub (Secondary Project)
| Need | File |
|------|------|
| Overview | `docs/projects/dev-hub/README.md` |
| Design | `docs/projects/dev-hub/DESIGN.md` |
| Plan | `.dev/roadmap/dev-hub-plan.md` |

---

## Rules & Workflows

### Universal Rules (All AIs)
| Rule | File | Trigger |
|------|------|---------|
| Collaboration | `.agent/rules/01-collaboration.md` | Always |
| Git Workflow | `.agent/rules/02-git-workflow.md` | Always |
| Communication | `.agent/rules/03-communication.md` | Always |
| Validation | `.agent/rules/04-validation.md` | After coding |
| Documentation | `.agent/rules/05-documentation.md` | End of task |

### Workflows
| Workflow | File | When |
|----------|------|------|
| New Feature | `.agent/workflows/feature.md` | Adding functionality |
| Bug Fix | `.agent/workflows/bugfix.md` | Fixing issues |
| Release | `.agent/workflows/release.md` | Version bump |
| Session Start | `.agent/workflows/session-start.md` | Every session |

---

## Templates

### Backend Templates
```
.dev/patterns/backend/templates/
├── router.py.tpl           # FastAPI router
├── schema.py.tpl           # Pydantic schemas
├── model.py.tpl            # SQLAlchemy model
├── test.py.tpl             # Pytest tests
└── migration.py.tpl        # Alembic migration
```

### Frontend Templates
```
.dev/patterns/frontend/templates/
├── component.tsx.tpl       # React component
├── store.ts.tpl            # Zustand store
├── hook.ts.tpl             # Custom hook
└── test.tsx.tpl            # Vitest test
```

---

## Documentation (Human-Readable)

| Category | Location |
|----------|----------|
| Getting Started | `docs/getting-started/` |
| Developer Guide | `docs/developer-guide/` |
| Architecture | `docs/architecture/` |
| API Reference | `docs/api-reference/` |
| User Guide | `docs/user-guide/` |

---

## Journal & Tracking

| File | Purpose |
|------|---------|
| `.dev/journal/YYYY-MM/YYYY-MM-DD.md` | Daily work log |
| `.dev/testing/test-status.md` | Test validation status |
| `.dev/roadmap/current-sprint.md` | Sprint progress |
| `.dev/roadmap/backlog/` | Future features |

---

## Loading Strategy

### Minimal (Quick questions)
```
Load: ATLAS.md only
```

### Standard (Development work)
```
Load: ATLAS.md + .dev/index.md + relevant patterns
```

### Full Context (Architecture decisions)
```
Load: ATLAS.md + .dev/index.md + .dev/context/* + docs/architecture/
```

---

**Version:** 1.0
**Updated:** 2025-11-28
**Purpose:** CAG (Context-Aware Generation) for efficient token usage
