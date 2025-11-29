# Rule 09: Mock Data via Seed Scripts

**Priority:** MANDATORY
**Applies to:** All AI agents creating test/demo data

---

## Rule

When creating mock data, demo data, or test fixtures:

**DO:**
- Create data via seed scripts in `apps/synapse/backend/app/scripts/`
- Use proper database transactions
- Follow existing seed patterns (see `seed_*.py` files)
- Create reproducible, consistent data

**DO NOT:**
- Invent data inline in code
- Hardcode mock values in tests without fixtures
- Create temporary data that bypasses the database
- Use random data without seeding the random generator

---

## Why

1. **Reproducibility** - Same data every time for consistent testing
2. **Database Integrity** - Proper relationships and constraints
3. **Traceability** - Know exactly what data exists
4. **Demo Ready** - Consistent data for presentations

---

## Examples

### Correct: Seed Script

```python
# apps/synapse/backend/app/scripts/seed_demo_instruments.py

from app.core.database import get_db
from app.models import Asset, Project

def seed_demo_instruments():
    """Create demo instruments for testing."""
    db = next(get_db())

    project = db.query(Project).filter_by(code="DEMO").first()
    if not project:
        project = Project(code="DEMO", name="Demo Project")
        db.add(project)

    instruments = [
        {"tag": "FT-001", "description": "Flow Transmitter", "type": "Instrument"},
        {"tag": "PT-001", "description": "Pressure Transmitter", "type": "Instrument"},
    ]

    for inst in instruments:
        asset = Asset(project_id=project.id, **inst)
        db.add(asset)

    db.commit()
    print(f"Created {len(instruments)} demo instruments")

if __name__ == "__main__":
    seed_demo_instruments()
```

### Incorrect: Inline Mock Data

```python
# DON'T DO THIS
def test_something():
    # Bad: inventing data inline
    asset = Asset(tag="TEST-123", description="fake thing")
    db.add(asset)
```

---

## Enforcement

- Code review: Reject PRs with inline mock data
- Tests: Use pytest fixtures from conftest.py
- Demo: Always use seed scripts before presentations

---

## Related Files

| File | Purpose |
|------|---------|
| `app/scripts/seed_*.py` | Seed script templates |
| `tests/conftest.py` | Pytest fixtures |
| `app/scripts/reset_db.py` | Database reset + reseed |
