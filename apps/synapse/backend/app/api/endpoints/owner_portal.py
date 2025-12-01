from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.analytics_database import get_analytics_db
from app.schemas.owner import (
    ArchitectureCheckpoint,
    HealthScorecard,
    TechDebtItem,
    TestRun,
)

router = APIRouter()


@router.get("/health-scorecards", response_model=list[HealthScorecard])
def list_health_scorecards(
    version: str | None = Query(default=None, description="Filter by version (e.g., v0.2.2)"),
    area: str | None = Query(
        default=None, description="Filter by area (backend, frontend, infra, etc.)"
    ),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_analytics_db),
):
    sql = """
        SELECT id, created_at, version, area, reliability, dx, observability, ux, notes
        FROM owner.health_scorecards
        WHERE 1=1
    """
    params = {"limit": limit}

    if version:
        sql += " AND version = :version"
        params["version"] = version
    if area:
        sql += " AND area = :area"
        params["area"] = area

    sql += " ORDER BY created_at DESC LIMIT :limit"

    rows = db.execute(text(sql), params).mappings().all()
    return [HealthScorecard(**row) for row in rows]


@router.get("/test-runs", response_model=list[TestRun])
def list_test_runs(
    version: str | None = Query(default=None),
    component: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_analytics_db),
):
    sql = """
        SELECT id, started_at, finished_at, project, component, version, suite,
               total, passed, failed, skipped, report_url, origin
        FROM owner.test_runs
        WHERE 1=1
    """
    params = {"limit": limit}

    if version:
        sql += " AND version = :version"
        params["version"] = version
    if component:
        sql += " AND component = :component"
        params["component"] = component

    sql += " ORDER BY started_at DESC LIMIT :limit"

    rows = db.execute(text(sql), params).mappings().all()
    # Derive passRate client-side later; keep raw counts here.
    return [TestRun(**row) for row in rows]


@router.get("/tech-debt-items", response_model=list[TechDebtItem])
def list_tech_debt_items(
    status: str | None = Query(default=None),
    impact: str | None = Query(default=None),
    area: str | None = Query(default=None),
    target_version: str | None = Query(default=None),
    limit: int = Query(default=200, ge=1, le=1000),
    db: Session = Depends(get_analytics_db),
):
    sql = """
        SELECT id, code, created_at, updated_at, area, title, context, impact, effort, risk,
               type, status, target_version, source_file
        FROM owner.tech_debt_items
        WHERE 1=1
    """
    params = {"limit": limit}

    if status:
        sql += " AND status = :status"
        params["status"] = status
    if impact:
        sql += " AND impact = :impact"
        params["impact"] = impact
    if area:
        sql += " AND area = :area"
        params["area"] = area
    if target_version:
        sql += " AND target_version = :target_version"
        params["target_version"] = target_version

    sql += " ORDER BY created_at DESC LIMIT :limit"

    rows = db.execute(text(sql), params).mappings().all()
    return [TechDebtItem(**row) for row in rows]


@router.get("/architecture-checkpoints", response_model=list[ArchitectureCheckpoint])
def list_architecture_checkpoints(
    version: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_analytics_db),
):
    sql = """
        SELECT id, version, planned_at, completed_at, status, summary, main_risks, main_decisions
        FROM owner.architecture_checkpoints
        WHERE 1=1
    """
    params = {"limit": limit}

    if version:
        sql += " AND version = :version"
        params["version"] = version

    sql += " ORDER BY COALESCE(planned_at, completed_at) DESC NULLS LAST, version DESC LIMIT :limit"

    rows = db.execute(text(sql), params).mappings().all()
    return [ArchitectureCheckpoint(**row) for row in rows]
