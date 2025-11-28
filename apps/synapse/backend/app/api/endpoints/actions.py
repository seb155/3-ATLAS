
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.action_log import ActionLog, ActionStatus, ActionType
from app.schemas.action_log import ActionLogResponse
from app.services.action_logger import ActionLogger

router = APIRouter(
    prefix="/api/v1/actions",
    tags=["actions"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=list[ActionLogResponse])
def get_actions(
    project_id: str | None = None,
    parent_id: UUID | None = None,
    limit: int = 1000,
    db: Session = Depends(get_db),
):
    """
    Fetch action logs.
    """
    """
    Fetch action logs.
    """
    return ActionLogger.get_logs(db, project_id, limit, parent_id)


@router.delete("/")
def clear_actions(db: Session = Depends(get_db)):
    """
    Clear all action logs.
    """
    db.query(ActionLog).delete()
    db.commit()
    return {"status": "Logs Cleared"}


@router.post("/{action_id}/rollback")
def rollback_action(action_id: UUID, db: Session = Depends(get_db)):
    """
    Rollback a specific action.
    Currently only supports rolling back CREATE actions (deleting the entity).
    """
    log = db.query(ActionLog).filter(ActionLog.id == action_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Action log not found")

    if log.status == ActionStatus.ROLLED_BACK:
        raise HTTPException(status_code=400, detail="Action already rolled back")

    # Implement rollback logic
    if log.action_type == ActionType.CREATE:
        if log.entity_type == "NODE":
            # Delete the node
            from app.models.metamodel import MetamodelEdge, MetamodelNode

            # First delete connected edges
            db.query(MetamodelEdge).filter(
                (MetamodelEdge.source_node_id == log.entity_id)
                | (MetamodelEdge.target_node_id == log.entity_id)
            ).delete()
            # Then delete node
            db.query(MetamodelNode).filter(MetamodelNode.id == str(log.entity_id)).delete()
        elif log.entity_type == "EDGE":
            from app.models.metamodel import MetamodelEdge

            db.query(MetamodelEdge).filter(MetamodelEdge.id == str(log.entity_id)).delete()

    log.status = ActionStatus.ROLLED_BACK
    db.commit()

    return {"status": "Action rolled back", "id": action_id}
