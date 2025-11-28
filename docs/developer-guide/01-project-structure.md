# Project Structure

Understand the SYNAPSE codebase organization.

---

## Monorepo Overview

```
EPCB-Tools/                      # Monorepo root
├── .agent/                      # AI workflows & rules
├── workspace/                   # Dev infrastructure
│   ├── docker-compose.yml
│   ├── databases/postgres/init/
│   └── scripts/
│
├── apps/synapse/                # SYNAPSE application
│   ├── backend/
│   ├── frontend/
│   └── docker-compose.dev.yml
│
├── docs/                        # Documentation
├── .dev/                        # Dev tracking (journal, ADR, roadmap)
├── dev.ps1, stop.ps1           # Quick start scripts
└── README.md
```

---

## Backend Structure

```
apps/synapse/backend/
├── app/
│   ├── main.py                  # FastAPI app entry
│   ├── api/endpoints/           # REST endpoints
│   │   ├── assets.py
│   │   ├── cables.py
│   │   ├── rules.py
│   │   └── projects.py
│   ├── models/                  # SQLAlchemy models
│   │   ├── models.py            # Core models (Asset, Project)
│   │   └── rules.py             # Rule models
│   ├── schemas/                 # Pydantic schemas
│   │   ├── asset.py
│   │   ├── rule.py
│   │   └── project.py
│   ├── services/                # Business logic
│   │   ├── rule_engine.py       # Core automation
│   │   ├── rule_executor.py
│   │   ├── cable_sizing.py
│   │   └── ingestion_service.py
│   ├── core/                    # Config, DB, security
│   │   ├── config.py
│   │   ├── database.py
│   │   └── security.py
│   └── scripts/                 # Seeding, utilities
├── Dockerfile
├── requirements.txt
└── alembic/                     # Database migrations
    └── versions/
```

### Backend Patterns

**Router Pattern:**
```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_project

router = APIRouter(prefix="/assets", tags=["assets"])

@router.get("/{asset_id}")
async def get_asset(
    asset_id: UUID,
    db: Session = Depends(get_db),
    project = Depends(get_current_project)
):
    # Always filter by project_id (multi-tenancy)
    return db.query(Asset).filter(
        Asset.id == asset_id,
        Asset.project_id == project.id
    ).first()
```

**Key patterns:**
- Always filter by `project_id` for multi-tenancy
- Use Pydantic schemas for request/response validation
- Use `Depends()` for dependency injection
- Async/await for database operations

---

## Frontend Structure

```
apps/synapse/frontend/
├── src/
│   ├── App.tsx                  # Main app component
│   ├── pages/                   # Main views
│   │   ├── Dashboard.tsx
│   │   ├── EngineeringExplorer.tsx
│   │   ├── RulesManagement.tsx
│   │   └── Ingestion.tsx
│   ├── components/              # Reusable components
│   │   ├── Layout.tsx
│   │   ├── DevConsole.tsx
│   │   └── auth/LoginScreen.tsx
│   ├── store/                   # Zustand state
│   │   ├── useAppStore.ts
│   │   ├── useAuthStore.ts
│   │   └── useProjectStore.ts
│   ├── services/                # API clients
│   │   └── axiosConfig.ts
│   └── types/                   # TypeScript types
├── index.tsx                    # Entry point
├── package.json
├── vite.config.ts
└── Dockerfile.dev               # Dev server
```

### Frontend Patterns

**Zustand Store:**
```typescript
import { create } from 'zustand';

interface AppState {
  assets: Asset[];
  selectedAsset: Asset | null;
  setAssets: (assets: Asset[]) => void;
  selectAsset: (asset: Asset) => void;
}

export const useAppStore = create<AppState>((set) => ({
  assets: [],
  selectedAsset: null,
  setAssets: (assets) => set({ assets }),
  selectAsset: (asset) => set({ selectedAsset: asset }),
}));
```

**Key patterns:**
- TypeScript strict mode
- Functional components only
- Zustand for global state
- TailwindCSS for styling

---

## Database

### Schema Overview

**12 Core Tables:**

| Table | Purpose |
|-------|---------|
| `projects` | Multi-tenancy isolation |
| `users` | Authentication |
| `assets` | Equipment/instruments |
| `lbs_nodes` | Location hierarchy |
| `connections` | Asset relationships |
| `rule_definitions` | Automation rules |
| `rule_executions` | Rule history |
| `cables` | Electrical cables |
| `packages` | Asset grouping |
| `action_logs` | Audit trail |

### Migrations (Alembic)

**Create migration:**
```bash
docker exec synapse-backend-1 alembic revision --autogenerate -m "add my_table"
```

**Apply migration:**
```bash
docker exec synapse-backend-1 alembic upgrade head
```

**Rollback:**
```bash
docker exec synapse-backend-1 alembic downgrade -1
```

### Model Changes (3-Step Process)

1. **Update model** in `app/models/`
2. **Generate migration** with Alembic
3. **Update Pydantic schema** in `app/schemas/`

**Never use raw SQL** - always use Alembic migrations.

---

## Testing

### Backend Tests (pytest)

```
apps/synapse/backend/tests/
├── test_assets.py
├── test_rules.py
├── test_validation.py
└── conftest.py
```

**Run tests:**
```bash
docker exec synapse-backend-1 pytest
docker exec synapse-backend-1 pytest -v  # verbose
docker exec synapse-backend-1 pytest tests/test_rules.py  # specific file
```

### Frontend Tests (Playwright)

```
apps/synapse/frontend/e2e/
├── basic.spec.ts
└── auth.spec.ts
```

**Run E2E tests:**
```bash
cd apps/synapse/frontend
npx playwright test
npx playwright test --ui  # with UI
```

---

## Adding Features

### Add Backend Endpoint

1. Create `/app/api/endpoints/my_feature.py`
2. Define routes with FastAPI
3. Add to `/app/main.py`:
   ```python
   from app.api.endpoints import my_feature
   app.include_router(my_feature.router)
   ```

### Add Frontend Page

1. Create `/src/pages/MyFeature.tsx`
2. Add route in `App.tsx`
3. Add navigation link in `Layout.tsx`

### Add Database Table

1. Create model in `/app/models/`
2. Generate migration: `alembic revision --autogenerate -m "add table"`
3. Apply: `alembic upgrade head`
4. Create Pydantic schema in `/app/schemas/`

---

## Configuration Files

**Backend:**
- `.env` - Environment variables
- `requirements.txt` - Python dependencies
- `alembic.ini` - Migration config

**Frontend:**
- `package.json` - Node dependencies
- `vite.config.ts` - Build config
- `tsconfig.json` - TypeScript config

---

## Related Documentation

- [Deployment](06-deployment.md) - Docker, production
- [Code Guidelines](../contributing/code-guidelines.md) - Standards
- [Git Workflow](../contributing/git-workflow.md) - Contributing

---

**Need details?** Explore the code or check `.dev/context/project-state.md`
