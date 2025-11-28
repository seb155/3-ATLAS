import enum
import uuid
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, ForeignKey, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import backref, relationship

from app.core.database import Base
from app.models.metamodel import DisciplineType


class ActionType(str, enum.Enum):
    RULE_EXECUTION = "RULE_EXECUTION"
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    LINK = "LINK"
    ERROR = "ERROR"


class ActionStatus(str, enum.Enum):
    COMPLETED = "COMPLETED"
    ROLLED_BACK = "ROLLED_BACK"
    FAILED = "FAILED"


class ActionLog(Base):
    __tablename__ = "action_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(String, nullable=True)  # Can be null for global actions
    parent_id = Column(UUID(as_uuid=True), ForeignKey("action_logs.id"), nullable=True)

    action_type = Column(SQLEnum(ActionType), nullable=False)
    entity_type = Column(String, nullable=True)  # e.g., "NODE", "EDGE"
    entity_id = Column(UUID(as_uuid=True), nullable=True)

    discipline = Column(SQLEnum(DisciplineType), nullable=True)

    description = Column(String, nullable=False)
    details = Column(JSON, nullable=True)

    status = Column(SQLEnum(ActionStatus), default=ActionStatus.COMPLETED)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    children = relationship("ActionLog", backref=backref("parent", remote_side=[id]))
