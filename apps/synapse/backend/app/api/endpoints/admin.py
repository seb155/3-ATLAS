"""
Admin endpoints for activity logs, seed data, and administrative actions.
"""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy import desc, or_
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.models.action_log import ActionLog
from app.models.workflow import WorkflowEvent, BatchOperation
from app.models.models import Asset
from app.models.cables import Cable
from app.models.metamodel import MetamodelNode
from app.models.auth import User

router = APIRouter()


@router.get("/activity")
def get_activity_logs(
    project_id: str = Header(..., alias="X-Project-ID"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    action_type: Optional[str] = Query(None),
    entity_type: Optional[str] = Query(None),
    hours: Optional[int] = Query(None, description="Filter logs from last N hours"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get activity logs (action_logs + workflow_events) for the project.
    Combined view of all system activity.
    """
    # Query action logs
    action_query = db.query(ActionLog).filter(ActionLog.project_id == project_id)

    if action_type:
        action_query = action_query.filter(ActionLog.action_type == action_type)
    if entity_type:
        action_query = action_query.filter(ActionLog.entity_type == entity_type)
    if hours:
        since = datetime.utcnow() - timedelta(hours=hours)
        action_query = action_query.filter(ActionLog.timestamp >= since)

    action_logs = action_query.order_by(desc(ActionLog.timestamp)).offset(offset).limit(limit).all()

    # Query workflow events
    workflow_query = db.query(WorkflowEvent).filter(WorkflowEvent.project_id == project_id)
    if hours:
        since = datetime.utcnow() - timedelta(hours=hours)
        workflow_query = workflow_query.filter(WorkflowEvent.timestamp >= since)

    workflow_events = workflow_query.order_by(desc(WorkflowEvent.timestamp)).offset(offset).limit(limit).all()

    # Format response
    logs = []

    for log in action_logs:
        logs.append({
            "id": log.id,
            "type": "action",
            "action_type": log.action_type.value if log.action_type else None,
            "entity_type": log.entity_type,
            "entity_id": str(log.entity_id) if log.entity_id else None,
            "description": log.description,
            "details": log.details,
            "timestamp": log.timestamp.isoformat() if log.timestamp else None,
        })

    for event in workflow_events:
        logs.append({
            "id": event.id,
            "type": "workflow",
            "action_type": event.action_type.value if event.action_type else None,
            "entity_type": event.entity_type,
            "entity_id": event.entity_id,
            "entity_tag": event.entity_tag,
            "description": event.message,
            "details": event.details,
            "timestamp": event.timestamp.isoformat() if event.timestamp else None,
            "correlation_id": event.correlation_id,
        })

    # Sort combined by timestamp
    logs.sort(key=lambda x: x["timestamp"] or "", reverse=True)

    return {
        "logs": logs[:limit],
        "total": len(logs),
        "offset": offset,
        "limit": limit,
    }


@router.get("/stats")
def get_admin_stats(
    project_id: str = Header(..., alias="X-Project-ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get statistics for admin dashboard."""
    asset_count = db.query(Asset).filter(Asset.project_id == project_id).count()
    cable_count = db.query(Cable).filter(Cable.project_id == project_id).count()
    log_count = db.query(ActionLog).filter(ActionLog.project_id == project_id).count()
    workflow_count = db.query(WorkflowEvent).filter(WorkflowEvent.project_id == project_id).count()

    return {
        "assets": asset_count,
        "cables": cable_count,
        "action_logs": log_count,
        "workflow_events": workflow_count,
    }


@router.post("/seed-demo")
def seed_demo_data(
    project_id: str = Header(..., alias="X-Project-ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Seed demo data for the project.
    Creates sample assets and rules for demonstration.
    """
    from app.scripts.seed_demo import seed_demo_data as run_seed

    try:
        result = run_seed(db, project_id)
        return {"status": "success", "message": "Demo data seeded", "details": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/execute-rules")
def execute_all_rules(
    project_id: str = Header(..., alias="X-Project-ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Execute all rules for the project."""
    from app.services.rule_engine import RuleEngine

    try:
        result = RuleEngine.apply_rules(db, project_id)
        return {
            "status": "success",
            "rules_executed": result.get("total_rules", 0),
            "actions_taken": result.get("actions_taken", 0),
            "details": result,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.delete("/clear-data")
def clear_project_data(
    project_id: str = Header(..., alias="X-Project-ID"),
    confirm: bool = Query(False, description="Must be true to confirm deletion"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Clear all data from the project (assets, cables, logs, etc.).
    Keeps the project itself and rules.
    """
    if not confirm:
        return {"status": "error", "message": "Must set confirm=true to proceed"}

    # Delete in FK order
    deleted = {}
    deleted["workflow_events"] = db.query(WorkflowEvent).filter(WorkflowEvent.project_id == project_id).delete()
    deleted["batch_operations"] = db.query(BatchOperation).filter(BatchOperation.project_id == project_id).delete()
    deleted["action_logs"] = db.query(ActionLog).filter(ActionLog.project_id == project_id).delete()
    deleted["cables"] = db.query(Cable).filter(Cable.project_id == project_id).delete()
    deleted["metamodel_nodes"] = db.query(MetamodelNode).filter(MetamodelNode.project_id == project_id).delete()
    deleted["assets"] = db.query(Asset).filter(Asset.project_id == project_id).delete()

    db.commit()

    return {
        "status": "success",
        "message": "Project data cleared",
        "deleted": deleted,
    }
