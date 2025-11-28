# Prompt Template: New API Endpoint

**Purpose:** Generate FastAPI endpoint following project patterns
**Version:** 1.0
**Pattern Reference:** `apps/synapse/backend/app/routers/cables.py`
**Shared Resources:** `.claude/skills/api-endpoint/` (Templates shared with Claude Code)

---

## Template Files

**Location:** `.claude/skills/api-endpoint/templates/`
- `router.py.template` - FastAPI router with multi-tenancy
- `schema.py.template` - Pydantic request/response models
- `test.py.template` - Pytest tests with fixtures

---

## Template

```
Create a FastAPI endpoint with the following characteristics:

**Endpoint:** [METHOD] /api/v1/[resource]/
**Description:** [Functional description]

**Requirements:**
1. **Multi-tenancy:** Filter by project_id from X-Project-ID header
2. **Authentication:** Require current_user (JWT via get_current_user dependency)
3. **Pydantic schema:** Request + Response models with serialize_by_alias=True
4. **Type hints:** All parameters and return types
5. **Error handling:** Use custom exceptions (NotFoundError, ValidationError, DuplicateError)
6. **Logging:** Log request/response to Loki (via middleware)
7. **Tests:** pytest with 80%+ coverage
8. **API Conventions:** Trailing slash on collection endpoints

**Example Response:**
```json
{
  "id": "uuid",
  "project_id": "uuid",
  "field1": "value1",
  "field2": 123,
  "created_at": "2025-11-25T10:00:00Z",
  "updated_at": "2025-11-25T10:00:00Z"
}
```

**File Structure:**
- `app/routers/[resource].py` - API endpoint
- `app/schemas/[resource].py` - Pydantic models
- `app/models/[resource].py` - SQLAlchemy model (if new table)
- `tests/test_[resource].py` - pytest tests

**Follow patterns from:** `app/routers/cables.py`, `app/models/models.py`

**Code Guidelines:** See `docs/contributing/code-guidelines.md`
```

---

## Example Usage

### User Fills Template:
```
Create a FastAPI endpoint with the following characteristics:

**Endpoint:** POST /api/v1/import_logs/
**Description:** Log CSV import operations with status and statistics

**Requirements:**
[...as above...]

**Example Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "project_id": "12c634bd-e786-48f2-8ef3-8d0957a31bf5",
  "filename": "BBA_export.csv",
  "status": "completed",
  "rows_imported": 100,
  "rows_failed": 2,
  "created_at": "2025-11-25T10:00:00Z"
}
```
```

### AI Generates:

**1. SQLAlchemy Model** (`app/models/import_logs.py`):
```python
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from .database import Base
import uuid
from datetime import datetime

class ImportLog(Base):
    __tablename__ = "import_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    filename = Column(String, nullable=False)
    status = Column(String, nullable=False)  # pending, completed, failed
    rows_imported = Column(Integer, default=0)
    rows_failed = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
```

**2. Pydantic Schemas** (`app/schemas/import_logs.py`):
```python
from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime

class ImportLogCreate(BaseModel):
    filename: str
    status: str
    rows_imported: int = 0
    rows_failed: int = 0

class ImportLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    project_id: UUID
    filename: str
    status: str
    rows_imported: int
    rows_failed: int
    created_at: datetime
```

**3. API Router** (`app/routers/import_logs.py`):
```python
from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ..core.database import get_db
from ..core.auth import get_current_user
from ..models.auth import User
from ..models.import_logs import ImportLog
from ..schemas.import_logs import ImportLogCreate, ImportLogResponse

router = APIRouter(
    prefix="/api/v1/import_logs",
    tags=["import_logs"]
)

@router.post("/", response_model=ImportLogResponse)
def create_import_log(
    log: ImportLogCreate,
    project_id: UUID = Header(..., alias="X-Project-ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new import log."""
    db_log = ImportLog(
        project_id=str(project_id),
        **log.dict()
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

@router.get("/", response_model=List[ImportLogResponse])
def list_import_logs(
    project_id: UUID = Header(..., alias="X-Project-ID"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List import logs for a project."""
    logs = db.query(ImportLog).filter(
        ImportLog.project_id == str(project_id)
    ).offset(skip).limit(limit).all()
    return logs
```

**4. Tests** (`tests/test_import_logs.py`):
```python
import pytest
from uuid import uuid4

def test_create_import_log(client, auth_headers, project_id):
    """Test creating an import log."""
    response = client.post(
        "/api/v1/import_logs/",
        json={
            "filename": "test.csv",
            "status": "completed",
            "rows_imported": 100,
            "rows_failed": 2
        },
        headers={**auth_headers, "X-Project-ID": str(project_id)}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test.csv"
    assert data["status"] == "completed"
    assert data["rows_imported"] == 100

def test_list_import_logs(client, auth_headers, project_id):
    """Test listing import logs."""
    # Create a log first
    client.post(
        "/api/v1/import_logs/",
        json={"filename": "test.csv", "status": "completed"},
        headers={**auth_headers, "X-Project-ID": str(project_id)}
    )

    # List logs
    response = client.get(
        "/api/v1/import_logs/",
        headers={**auth_headers, "X-Project-ID": str(project_id)}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["filename"] == "test.csv"

def test_multi_tenancy_isolation(client, auth_headers, project_id):
    """Test that logs are isolated by project."""
    other_project_id = uuid4()

    # Create log in project_id
    client.post(
        "/api/v1/import_logs/",
        json={"filename": "test.csv", "status": "completed"},
        headers={**auth_headers, "X-Project-ID": str(project_id)}
    )

    # List logs in other_project_id
    response = client.get(
        "/api/v1/import_logs/",
        headers={**auth_headers, "X-Project-ID": str(other_project_id)}
    )
    assert response.status_code == 200
    assert len(response.json()) == 0  # Should be empty
```

**5. Alembic Migration**:
```bash
# Run: docker exec synapse-backend-1 alembic revision -m "add import_logs table"
# Then edit the generated migration file
```

---

## Checklist for AI

Before presenting code, verify:
- [ ] Multi-tenancy filter present (project_id)
- [ ] JWT auth dependency included (current_user)
- [ ] Type hints on all parameters and returns
- [ ] Pydantic models use serialize_by_alias=True
- [ ] Error handling implemented (if applicable)
- [ ] Tests cover CRUD operations
- [ ] Tests include multi-tenancy check
- [ ] Tests achieve >70% coverage
- [ ] Trailing slash on collection endpoint
- [ ] Follows patterns from existing routers

---

**Version:** 1.0
**Last Updated:** 2025-11-25
