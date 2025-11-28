# Code Guidelines

Standards and conventions for SYNAPSE development.

---

## General Principles

1. **Keep it simple** - Prefer clarity over cleverness
2. **Follow existing patterns** - Match the codebase style
3. **Document complex logic** - Code explains how, comments explain why
4. **Test your changes** - Write tests for new features

---

## Naming Conventions (CRITICAL)

### Rule Names

**NO UNDERSCORES.** Use natural language with "Source: Description" format.

- `FIRM: Centrifugal Pumps require Electric Motor`
- `COUNTRY-CA: 600V Standard Voltage`
- `PROJECT-GoldMine: Use ABB Motors`
- `CLIENT-AuruMax: Siemens PLC Only`

**WRONG:** `firm_motor_rule`, `country_ca_voltage`

### Code Naming

**Python (backend):**
- Files: `snake_case.py`
- Classes: `PascalCase`
- Functions/variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`

**TypeScript (frontend):**
- Files: `PascalCase.tsx` (components), `camelCase.ts` (utilities)
- Components: `PascalCase`
- Functions/variables: `camelCase`
- Constants: `UPPER_SNAKE_CASE`

**Database:**
- Tables: `plural_snake_case` (e.g., `assets`, `rule_definitions`)
- Columns: `snake_case`

---

## API Patterns (CRITICAL)

### Trailing Slash Rule

**ALWAYS** include trailing slash for collection endpoints.

```javascript
// CORRECT
axios.get('/api/v1/assets/')
axios.get('/api/v1/rules/')

// WRONG - Causes 307 Redirect & Auth Loss
axios.get('/api/v1/assets')
```

### Pydantic Serialization

**ALWAYS** add `serialize_by_alias: True` to Response schemas.

```python
class AssetResponse(BaseModel):
    id: str
    location_id: str = Field(alias="locationId")

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
        "serialize_by_alias": True  # CRITICAL
    }
```

### Required Headers

```javascript
const config = {
    headers: {
        'Authorization': `Bearer ${token}`,
        'X-Project-ID': projectId
    }
};
```

### Error Handling

```typescript
try {
    const response = await axios.get('/api/v1/assets/', config);
    return response.data;
} catch (error) {
    if (axios.isAxiosError(error)) {
        if (error.response?.status === 401) {
            useAuthStore.getState().logout();
        } else if (error.response?.status === 422) {
            console.error('Validation:', error.response.data.detail);
        }
    }
}
```

**Common Status Codes:**

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Return data |
| 307 | Redirect | Check trailing slash! |
| 401 | Unauthorized | Logout, redirect |
| 422 | Validation Error | Show errors |
| 500 | Server Error | Check logs |

---

## File Structure Conventions

**Backend:**
- Endpoints: `app/api/endpoints/feature.py`
- Models: `app/models/models.py` or `app/models/feature.py`
- Services: `app/services/feature_service.py`
- Schemas: `app/schemas/feature.py`
- Tests: `tests/test_feature.py`

**Frontend:**
- Pages: `src/pages/FeatureName.tsx`
- Components: `src/components/ComponentName.tsx`
- State: `src/store/useFeatureStore.ts`
- Types: `src/types/feature.ts`

---

## Import Organization

**Backend:**
```python
# Standard library
import os
from typing import List

# Third-party
from fastapi import APIRouter
from sqlalchemy.orm import Session

# Local
from app.models.models import Asset
from app.services.rule_engine import RuleEngine
```

**Frontend:**
```typescript
// React
import React, { useState, useEffect } from 'react';

// Third-party
import { AgGridReact } from 'ag-grid-react';

// Local
import { useAppStore } from './store/useAppStore';
import { Layout } from './components/Layout';
```

---

## Rule Priority System

Rules execute in priority order. Higher priority overrides lower.

| Priority | Source | Example |
|----------|--------|---------|
| 100 | CLIENT | Client-specific preferences (highest) |
| 50 | PROJECT | Project-specific requirements |
| 30 | COUNTRY | National codes (voltage, CEC/NEC) |
| 10 | FIRM | Baseline company standards (lowest) |

### Decision Tree

```
Is this universal for ALL projects worldwide?
├─ YES → FIRM (Priority: 10)
└─ NO → Is it country-specific (voltage, codes)?
    ├─ YES → COUNTRY (Priority: 30)
    └─ NO → PROJECT (50) or CLIENT (100)
```

---

## Rule Action Types

### The 6 Action Types

| Action | Purpose | Example |
|--------|---------|---------|
| `CREATE_CHILD` | Create related asset | Pump → Motor |
| `SET_PROPERTY` | Update properties | Set voltage to 600V |
| `CREATE_CABLE` | Generate cable | Motor → MCC cable |
| `CREATE_PACKAGE` | Group assets | Pump + Motor package |
| `ALLOCATE_IO` | Assign PLC IO | Instrument → IO card |
| `VALIDATE` | Check constraints | Pump must have motor |

### CREATE_CHILD Example

```python
{
    "action_type": "CREATE_CHILD",
    "action": {
        "create_child": {
            "type": "MOTOR",
            "naming": "{parent_tag}-M",
            "relation": "powers",
            "inherit_properties": ["area", "system"],
            "properties": {
                "motor_type": "Electric",
                "enclosure": "TEFC"
            }
        }
    }
}
```

**Naming Patterns:**
- `{parent_tag}-M` → "310-PP-001-M" (Motor)
- `{parent_tag}-VFD` → "310-M-001-VFD" (VFD)

---

## Code Quality

### Early Returns (Avoid Deep Nesting)

```python
# BAD - Deep nesting
if asset.type == "PUMP":
    if asset.pump_type == "CENTRIFUGAL":
        if asset.area:
            create_motor(asset)

# GOOD - Early returns
def process_asset(asset):
    if asset.type != "PUMP": return
    if asset.pump_type != "CENTRIFUGAL": return
    if not asset.area: return
    create_motor(asset)
```

### Type Hints (Required)

```python
# GOOD
def get_asset(db: Session, asset_id: str) -> Asset | None:
    return db.query(Asset).filter(Asset.id == asset_id).first()

# BAD
def get_asset(db, asset_id):
    ...
```

---

## Backend (FastAPI)

- Use type hints
- Return Pydantic models
- Filter by `project_id` for multi-tenancy
- Use async/await for DB operations
- Handle errors with HTTPException

## Frontend (React)

- Use functional components
- TypeScript for all files
- Zustand for state management
- Extract reusable logic to hooks
- Use TailwindCSS for styling

## Database

- Always use Alembic migrations (never manual schema changes)
- Index foreign keys
- Use UUIDs for IDs
- Add `created_at`, `updated_at` timestamps

---

## Quick Reference Checklist

**When making API calls:**
- [ ] Add trailing slash for collection endpoints
- [ ] Include Authorization + X-Project-ID headers
- [ ] Handle 401/404/422 errors

**When creating schemas:**
- [ ] Add `serialize_by_alias: True`
- [ ] Add `Field(alias="camelCase")` for snake_case fields
- [ ] Keep frontend/backend enums synced

**When writing code:**
- [ ] Add type hints (Python) / interfaces (TypeScript)
- [ ] Keep functions small and focused
- [ ] Use early returns instead of nested ifs

---

## Git Workflow

See [Git Workflow](git-workflow.md) for branching, commits, PRs.
