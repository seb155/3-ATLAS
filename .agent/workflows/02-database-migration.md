---
description: Database migration workflow
---

# Database Migration

**Goal:** Safely apply database schema changes.

## 1. Make Model Changes

Edit: `apps/synapse/backend/app/models/models.py`

```python
class Asset(Base):
    # Add new field
    new_field: str = Column(String, nullable=True)
```

## 2. Generate Migration

```bash
docker exec synapse-backend-1 alembic revision --autogenerate -m "add new_field to assets"
```

## 3. Review Migration

Check: `apps/synapse/backend/alembic/versions/XXXX_add_new_field.py`

**Verify:**
- Upgrade logic correct
- Downgrade logic present
- No data loss

## 4. Apply Migration

```bash
docker exec synapse-backend-1 alembic upgrade head
```

## 5. Update Pydantic Schema

Update API schemas in endpoints or `app/schemas/`

## 6. Test

```bash
docker exec synapse-backend-1 pytest
```

## 7. Document

**If major change:**
- Create ADR in `.dev/decisions/`
- Update `docs/developer-guide/04-database.md`
- Log in `.dev/journal/`

**See:** `docs/developer-guide/04-database.md` for full guide
