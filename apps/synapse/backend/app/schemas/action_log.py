from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel

from app.models.action_log import ActionStatus, ActionType
from app.models.metamodel import DisciplineType


class ActionLogBase(BaseModel):
    project_id: str | None = None
    parent_id: UUID | None = None
    action_type: ActionType
    entity_type: str | None = None
    entity_id: UUID | None = None
    discipline: DisciplineType | None = None
    description: str
    details: dict[str, Any] | None = None
    status: ActionStatus = ActionStatus.COMPLETED


class ActionLogCreate(ActionLogBase):
    pass


class ActionLogResponse(ActionLogBase):
    id: UUID
    timestamp: datetime

    class Config:
        from_attributes = True
