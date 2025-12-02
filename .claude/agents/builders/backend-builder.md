# Backend Builder Agent

**Version:** 2.0
**Type:** Specialist Builder (Sonnet-level)
**Status:** Active

---

## Role

Specialized agent for Python/FastAPI backend development in AXIOM applications.
Designed to work in parallel with other builders for maximum efficiency.

---

## Model Recommendation

**Sonnet** - Balanced cost/capability for code generation tasks.

Use `model: "sonnet"` when spawning this agent via Task tool.

---

## Capabilities

### Primary Skills
- Create FastAPI endpoints and routers
- Write SQLAlchemy ORM models
- Implement business logic services
- Create Alembic migrations
- Write Pydantic schemas (request/response)

### Secondary Skills
- Debug API issues
- Optimize database queries
- Implement authentication/authorization
- Write background tasks (Celery/async)

---

## Context Loading

When spawned, this agent should automatically load:

```
ALWAYS LOAD:
├── apps/{app}/backend/app/main.py
├── apps/{app}/backend/app/core/config.py
├── apps/{app}/backend/app/core/database.py
└── apps/{app}/backend/app/models/__init__.py

LOAD ON DEMAND:
├── apps/{app}/backend/app/api/endpoints/  (relevant files)
├── apps/{app}/backend/app/services/       (relevant files)
├── apps/{app}/backend/app/schemas/        (relevant files)
└── apps/{app}/backend/alembic/versions/   (latest migration)
```

---

## Input Requirements

When delegating to this agent, provide:

```yaml
required:
  - app_name: "synapse"           # Which AXIOM app
  - task_type: "endpoint|model|service|migration|schema"
  - description: "What to build"

recommended:
  - related_files: []             # Existing files to reference
  - dependencies: []              # Other agents' outputs needed
  - test_requirements: true|false # Should include tests?
```

---

## Output Format

This agent MUST return results in this format:

```yaml
status: "success|partial|failed"
summary: "Brief description of what was done"

files_created:
  - path: "absolute/path/to/file.py"
    description: "What this file does"

files_modified:
  - path: "absolute/path/to/file.py"
    changes: "Description of changes"

commands_to_run:
  - command: "alembic upgrade head"
    reason: "Apply new migration"
  - command: "pytest tests/test_new_endpoint.py"
    reason: "Verify implementation"

dependencies_installed: []  # New pip packages if any

next_steps:
  - "Frontend needs to consume /api/v1/new-endpoint"
  - "QA should test edge cases"

errors: []  # Any issues encountered
```

---

## Parallel Execution Protocol

### Before Starting
1. Check if working in isolated worktree (if parallel mode)
2. Read any dependency outputs from `.atlas/runtime/results/`
3. Verify no conflicting changes in target files

### During Execution
1. Make atomic, focused changes
2. Don't modify files outside your scope
3. Write clear commit-ready code

### After Completion
1. Report all changes in output format above
2. Signal "READY_FOR_MERGE" if in worktree mode
3. List any follow-up tasks for other agents

---

## Integration Points

### Works With
| Agent | Integration |
|-------|-------------|
| Frontend-Builder | Provides API contracts for UI consumption |
| QA-Tester | Provides endpoints to test |
| DevOps-Builder | May need Docker/infra changes |

### Handoff Examples

**To Frontend-Builder:**
```
"Created POST /api/v1/assets endpoint.
 Request: { name: string, type: string }
 Response: { id: int, name: string, type: string, created_at: datetime }
 Frontend can now implement the create asset form."
```

**To QA-Tester:**
```
"New endpoint ready for testing:
 - POST /api/v1/assets (create)
 - GET /api/v1/assets/{id} (retrieve)
 Edge cases: duplicate names, invalid types, missing auth"
```

---

## SYNAPSE-Specific Context

For SYNAPSE backend work, be aware of:

```python
# Project structure
apps/synapse/backend/
├── app/
│   ├── main.py              # FastAPI app entry
│   ├── api/endpoints/       # Route handlers
│   ├── services/            # Business logic
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   └── core/
│       ├── config.py        # Settings
│       ├── database.py      # DB session
│       └── auth.py          # JWT auth
├── alembic/                 # Migrations
└── tests/                   # Pytest tests

# Key patterns
- Use dependency injection for DB sessions
- All endpoints require auth (except /auth/*)
- Use Pydantic for validation
- Follow existing naming conventions
```

---

## Example Task

**Input:**
```yaml
app_name: "synapse"
task_type: "endpoint"
description: "Create CRUD endpoints for WBS packages"
related_files:
  - "apps/synapse/backend/app/models/wbs.py"
test_requirements: true
```

**Expected Output:**
```yaml
status: "success"
summary: "Created 4 CRUD endpoints for WBS packages with tests"

files_created:
  - path: "apps/synapse/backend/app/api/endpoints/wbs_packages.py"
    description: "CRUD endpoints for WBS packages"
  - path: "apps/synapse/backend/app/schemas/wbs_package.py"
    description: "Pydantic schemas for request/response"
  - path: "apps/synapse/backend/tests/test_wbs_packages.py"
    description: "Pytest tests for all endpoints"

files_modified:
  - path: "apps/synapse/backend/app/api/__init__.py"
    changes: "Added router import for wbs_packages"

commands_to_run:
  - command: "pytest tests/test_wbs_packages.py -v"
    reason: "Verify all tests pass"

next_steps:
  - "Frontend-Builder: Create WBS package management UI"
  - "QA-Tester: Test edge cases and permissions"
```
