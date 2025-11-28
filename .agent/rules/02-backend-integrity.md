---
trigger: model_decision
description: Backend integrity - Database sync, API patterns, Multi-tenancy, Type hints
---

# Backend Integrity Protocol

**Purpose:** Ensure database models, migrations, API schemas, and multi-tenant patterns stay synchronized.

---

## 1. Database Model Sync

**Critical:** Backend models, API schemas, and migrations MUST stay in sync.

### Three files must stay in sync:
- `app/models/*.py` (SQLAlchemy ORM)
- `alembic/versions/*.py` (migrations)
- `app/schemas/*.py` (Pydantic validation)

### Workflow:
1. **Edit model** → Update SQLAlchemy model (`apps/synapse/backend/app/models/`)
2. **Generate migration** → `docker exec synapse-backend-1 alembic revision --autogenerate -m "description"`
3. **Review migration** → Check generated file in `alembic/versions/`
4. **Apply migration** → `docker exec synapse-backend-1 alembic upgrade head`
5. **Update schema** → Update Pydantic schema (`apps/synapse/backend/app/schemas/`)

### Key Files

| Type | Location |
|------|----------|
| Models | `apps/synapse/backend/app/models/` |
| Migrations | `apps/synapse/backend/alembic/versions/` |
| Schemas | `apps/synapse/backend/app/schemas/` |

### Common Mistakes
- ❌ Changing model without migration
- ❌ Manual SQL in psql
- ❌ Forgetting to update Pydantic schema

**Result:** Database/code mismatch = runtime errors

**Full guide:** See `/02-database-migration` workflow

---

## 2. Multi-Tenant API Filtering

**Every router endpoint MUST filter by project_id** for multi-tenancy.

### Pattern (REQUIRED):
```python
@router.get("/assets/")
async def list_assets(
    project_id: int = Depends(get_project_id),  # ← REQUIRED
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Asset).filter(
        Asset.project_id == project_id  # ← REQUIRED filter
    ).all()
```

### Single Item Endpoint:
```python
@router.get("/assets/{asset_id}")
async def get_asset(
    asset_id: UUID,
    project_id: int = Depends(get_project_id),  # ← REQUIRED
    db: Session = Depends(get_db)
):
    # Always filter by project_id
    return db.query(Asset).filter(
        Asset.id == asset_id,
        Asset.project_id == project_id  # ← REQUIRED filter
    ).first()
```

**Copy pattern from:** `apps/synapse/backend/app/routers/cables.py`

**Security:** Project-level isolation prevents cross-tenant data leaks

---

## 3. API Trailing Slash Convention

**REQUIRED:** All endpoints must end with `/`

### Correct:
- ✅ `/api/v1/assets/`
- ✅ `/api/v1/assets/{asset_id}/`

### Incorrect:
- ❌ `/api/v1/assets` (breaks JWT token passing)
- ❌ `/api/v1/assets/{asset_id}` (307 redirect loses auth headers)

**Technical reason:** FastAPI 307 redirects (without trailing slash) don't preserve Authorization headers.

---

## 4. Type Hints & Async

**Backend standards:**
- ✅ All parameters: type hints
- ✅ All DB queries: async (SQLAlchemy 2.0 async)
- ✅ All responses: Pydantic schemas
- ✅ All functions: return type annotations

### Example:
```python
async def create_asset(
    asset_data: AssetCreate,  # ← Pydantic schema
    project_id: int = Depends(get_project_id),
    db: AsyncSession = Depends(get_db)
) -> AssetResponse:  # ← Return type
    asset = Asset(**asset_data.dict(), project_id=project_id)
    db.add(asset)
    await db.commit()  # ← Async DB operation
    await db.refresh(asset)
    return asset
```

**Validation:** Run `mypy apps/synapse/backend` to check type hints

---

## Testing

**Before committing backend changes:**
```bash
# Test migrations
docker exec synapse-backend-1 alembic upgrade head

# Run tests
docker exec synapse-backend-1 pytest apps/synapse/backend/tests/

# Type check
docker exec synapse-backend-1 mypy app
```

---

## References

**Full guides:**
- Database migrations: `/02-database-migration` workflow
- API endpoint template: `/11-new-api-endpoint` workflow
- Code guidelines: `docs/contributing/code-guidelines.md`
- Project structure: `docs/developer-guide/01-project-structure.md`
