import uuid

from sqlalchemy import JSON, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=True)
    action = Column(String, nullable=False)  # CREATE, UPDATE, DELETE
    entity_type = Column(String, nullable=False)  # ASSET, LOCATION, etc.
    entity_id = Column(String, nullable=False)
    changes = Column(JSON)  # {field: {old: val, new: val}}
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="audit_logs")


class Snapshot(Base):
    __tablename__ = "snapshots"

    id = Column(String, primary_key=True, default=generate_uuid)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    data = Column(JSON, nullable=False)  # Full dump of project assets/locations
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by_id = Column(String, ForeignKey("users.id"), nullable=True)

    project = relationship("Project", back_populates="snapshots")
