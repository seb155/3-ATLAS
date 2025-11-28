from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class HealthScorecard(BaseModel):
    id: UUID
    created_at: datetime
    version: str
    area: str
    reliability: int
    dx: int
    observability: int
    ux: int
    notes: str | None = None

    class Config:
        from_attributes = True


class TestRun(BaseModel):
    id: UUID
    started_at: datetime
    finished_at: datetime | None = None
    project: str
    component: str
    version: str
    suite: str
    total: int
    passed: int
    failed: int
    skipped: int
    report_url: str | None = None
    origin: str

    class Config:
        from_attributes = True


class TechDebtItem(BaseModel):
    id: UUID
    code: str
    created_at: datetime
    updated_at: datetime
    area: str
    title: str
    context: str | None = None
    impact: str
    effort: str
    risk: str
    type: str
    status: str
    target_version: str | None = None
    source_file: str | None = None

    class Config:
        from_attributes = True


class ArchitectureCheckpoint(BaseModel):
    id: UUID
    version: str
    planned_at: datetime | None = None
    completed_at: datetime | None = None
    status: str
    summary: str | None = None
    main_risks: str | None = None
    main_decisions: str | None = None

    class Config:
        from_attributes = True
