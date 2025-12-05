# Skill: API Endpoint

Cree un endpoint API FastAPI complet avec router, schema, et tests.

## Usage

```text
/skill api-endpoint [resource]
```

## Templates Generes

1. `router.py` - Route FastAPI
2. `schema.py` - Schemas Pydantic
3. `test.py` - Tests pytest

## Exemple

```text
/skill api-endpoint notifications

Genere:
- app/api/v1/notifications.py
- app/schemas/notification.py
- tests/api/test_notifications.py
```

## Structure Router

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.{resource} import {Resource}Create, {Resource}Response
from app.services.{resource} import {Resource}Service

router = APIRouter(prefix="/{resources}", tags=["{resources}"])

@router.get("/", response_model=list[{Resource}Response])
async def list_{resources}(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    service = {Resource}Service(db)
    return await service.get_multi(skip=skip, limit=limit)

@router.post("/", response_model={Resource}Response)
async def create_{resource}(
    data: {Resource}Create,
    db: AsyncSession = Depends(get_db)
):
    service = {Resource}Service(db)
    return await service.create(data)

@router.get("/{{id}}", response_model={Resource}Response)
async def get_{resource}(
    id: int,
    db: AsyncSession = Depends(get_db)
):
    service = {Resource}Service(db)
    result = await service.get(id)
    if not result:
        raise HTTPException(status_code=404, detail="{Resource} not found")
    return result
```

## Structure Schema

```python
from pydantic import BaseModel
from datetime import datetime

class {Resource}Base(BaseModel):
    name: str
    description: str | None = None

class {Resource}Create({Resource}Base):
    pass

class {Resource}Update({Resource}Base):
    name: str | None = None

class {Resource}Response({Resource}Base):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

## Structure Test

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_{resource}(client: AsyncClient):
    response = await client.post(
        "/api/v1/{resources}/",
        json={{"name": "Test", "description": "Test description"}}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Test"

@pytest.mark.asyncio
async def test_list_{resources}(client: AsyncClient):
    response = await client.get("/api/v1/{resources}/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```
