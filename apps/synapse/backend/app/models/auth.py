import enum
import uuid

from sqlalchemy import JSON, Boolean, Column, DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    ENGINEER = "ENGINEER"
    VIEWER = "VIEWER"
    CLIENT = "CLIENT"


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(Enum(UserRole), default=UserRole.ENGINEER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    audit_logs = relationship("AuditLog", back_populates="user")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    action = Column(String, nullable=False)  # CREATE, UPDATE, DELETE
    target_type = Column(String, nullable=False)  # ASSET, PROJECT, etc.
    target_id = Column(String, nullable=False)
    details = Column(JSON)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="audit_logs")


class Client(Base):
    __tablename__ = "clients"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, unique=True, nullable=False)
    contact_email = Column(String)

    projects = relationship("Project", back_populates="client")


class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    client_id = Column(String, ForeignKey("clients.id"), nullable=False)
    country = Column(
        String, nullable=True
    )  # Country code for COUNTRY-level rules (e.g., "CA", "US")
    description = Column(String)
    status = Column(String, default="ACTIVE")  # ACTIVE, ARCHIVED, HOLD
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    client = relationship("Client", back_populates="projects")
    # snapshots = relationship("Snapshot", back_populates="project")
