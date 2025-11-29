"""
Workflow Event Sourcing & Versioning Models

This module implements the complete traceability system for SYNAPSE:
- WorkflowEvent: Event log for all actions (import, rule execution, manual edits)
- AssetVersion: Full snapshot versioning of assets
- PropertyChange: Granular field-level change tracking
- BatchOperation: Group operations for bulk rollback

Design based on: .dev/design/2025-11-28-whiteboard-session.md
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.core.database import Base


def generate_uuid():
    return str(uuid.uuid4())


# =============================================================================
# ENUMS
# =============================================================================


class LogLevel(str, enum.Enum):
    """Log severity levels"""

    TRACE = "TRACE"  # Technical details (debug only)
    DEBUG = "DEBUG"  # Developer info
    INFO = "INFO"  # Normal actions
    WARN = "WARN"  # Attention required
    ERROR = "ERROR"  # Recoverable error
    FATAL = "FATAL"  # Critical error


class LogSource(str, enum.Enum):
    """Source of the log event"""

    SYSTEM = "SYSTEM"  # Infrastructure (DB, WebSocket)
    IMPORT = "IMPORT"  # CSV/Excel import pipeline
    RULE = "RULE"  # Rule engine execution
    PACKAGE = "PACKAGE"  # Package generation
    USER = "USER"  # Manual user actions
    API = "API"  # External API calls
    ROLLBACK = "ROLLBACK"  # Rollback operations


class WorkflowActionType(str, enum.Enum):
    """Types of actions in the workflow"""

    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    EXECUTE = "EXECUTE"
    EXPORT = "EXPORT"
    IMPORT = "IMPORT"
    ROLLBACK = "ROLLBACK"
    VALIDATE = "VALIDATE"
    LINK = "LINK"


class WorkflowStatus(str, enum.Enum):
    """Status of a workflow event"""

    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ROLLED_BACK = "ROLLED_BACK"


class ChangeSource(str, enum.Enum):
    """Source of a change for versioning"""

    USER = "USER"  # Manual edit
    RULE = "RULE"  # Rule engine
    IMPORT = "IMPORT"  # CSV/Excel import
    API = "API"  # External API
    ROLLBACK = "ROLLBACK"  # Rollback operation
    SYSTEM = "SYSTEM"  # System operation


class BatchOperationType(str, enum.Enum):
    """Types of batch operations"""

    IMPORT = "IMPORT"
    RULE_EXECUTION = "RULE_EXECUTION"
    BULK_UPDATE = "BULK_UPDATE"
    BULK_DELETE = "BULK_DELETE"
    PACKAGE_GENERATION = "PACKAGE_GENERATION"


# =============================================================================
# WORKFLOW EVENTS (Central Event Log)
# =============================================================================


class WorkflowEvent(Base):
    """
    Central event log for all workflow actions.

    Every action in SYNAPSE (import, rule execution, manual edit, export)
    generates a WorkflowEvent for complete traceability.

    Supports:
    - Hierarchical events (parent_event_id for grouping)
    - Correlation tracking (correlation_id for related events)
    - Session grouping (session_id for user session)
    - Breakdown filtering (fbs_code, lbs_code, discipline)
    """

    __tablename__ = "workflow_events"

    # Primary Key
    id = Column(String, primary_key=True, default=generate_uuid)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    # Classification
    level = Column(SQLEnum(LogLevel), nullable=False, default=LogLevel.INFO, index=True)
    source = Column(SQLEnum(LogSource), nullable=False, index=True)
    action_type = Column(SQLEnum(WorkflowActionType), nullable=False, index=True)

    # Context
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)
    session_id = Column(String, nullable=True, index=True)

    # Target Entity
    entity_type = Column(String(50), nullable=True, index=True)  # ASSET, CABLE, RULE, PACKAGE
    entity_id = Column(String, nullable=True, index=True)
    entity_tag = Column(String(100), nullable=True)  # Human-readable (e.g., "LT-210-001")

    # Message
    message = Column(Text, nullable=False)
    details = Column(JSON, default=dict)  # Structured data (before/after, params)

    # Traceability
    parent_event_id = Column(String, ForeignKey("workflow_events.id"), nullable=True)
    correlation_id = Column(String, nullable=False, index=True)  # Group related events

    # Status
    status = Column(SQLEnum(WorkflowStatus), nullable=False, default=WorkflowStatus.COMPLETED)
    duration_ms = Column(Integer, nullable=True)
    error = Column(Text, nullable=True)

    # Breakdown Filtering (for multi-view queries)
    fbs_code = Column(String(20), nullable=True, index=True)  # Functional breakdown
    lbs_code = Column(String(20), nullable=True, index=True)  # Location breakdown
    discipline = Column(String(50), nullable=True, index=True)  # Engineering discipline
    package_code = Column(String(50), nullable=True, index=True)  # Work package

    # Relationships
    project = relationship("Project", foreign_keys=[project_id])
    user = relationship("User", foreign_keys=[user_id])
    parent_event = relationship("WorkflowEvent", remote_side=[id], backref="child_events")

    __table_args__ = (
        Index("ix_workflow_events_project_timestamp", "project_id", "timestamp"),
        Index("ix_workflow_events_correlation", "correlation_id"),
        Index("ix_workflow_events_entity", "entity_type", "entity_id"),
        Index("ix_workflow_events_session", "session_id"),
        Index("ix_workflow_events_breakdown", "fbs_code", "lbs_code", "discipline"),
    )

    def __repr__(self):
        return f"<WorkflowEvent {self.source.value}:{self.action_type.value} at {self.timestamp}>"


# =============================================================================
# ASSET VERSIONING (Full Snapshot)
# =============================================================================


class AssetVersion(Base):
    """
    Full snapshot versioning for assets.

    Each modification creates a new version with a complete JSON snapshot
    of the asset's state. Enables:
    - Full rollback to any previous version
    - Diff comparison between versions
    - Audit trail of all changes
    """

    __tablename__ = "asset_versions"

    # Primary Key
    id = Column(String, primary_key=True, default=generate_uuid)
    asset_id = Column(String, ForeignKey("assets.id"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)

    # Snapshot (complete asset state)
    snapshot = Column(JSON, nullable=False)  # {"tag": "MTR-210-001A", "power": 15, ...}

    # Metadata
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    created_by = Column(String, ForeignKey("users.id"), nullable=True)
    change_reason = Column(String(500), nullable=True)  # "Manual edit", "Rule execution"
    change_source = Column(SQLEnum(ChangeSource), nullable=False, default=ChangeSource.USER)
    event_id = Column(String, ForeignKey("workflow_events.id"), nullable=True)
    batch_id = Column(String, ForeignKey("batch_operations.id"), nullable=True, index=True)

    # Relationships
    asset = relationship("Asset", foreign_keys=[asset_id])
    creator = relationship("User", foreign_keys=[created_by])
    event = relationship("WorkflowEvent", foreign_keys=[event_id])
    batch = relationship("BatchOperation", foreign_keys=[batch_id], back_populates="versions")

    __table_args__ = (
        Index("ix_asset_versions_asset_version", "asset_id", "version_number"),
        Index("ix_asset_versions_batch", "batch_id"),
    )

    def __repr__(self):
        return f"<AssetVersion {self.asset_id} v{self.version_number}>"


# =============================================================================
# PROPERTY CHANGES (Field-Level Tracking)
# =============================================================================


class PropertyChange(Base):
    """
    Granular field-level change tracking.

    Tracks individual property changes for:
    - Property history timeline (e.g., power: 15kW -> 18.5kW -> 22kW)
    - Selective rollback of single properties
    - Field-level audit reports
    """

    __tablename__ = "property_changes"

    # Primary Key
    id = Column(String, primary_key=True, default=generate_uuid)
    asset_id = Column(String, ForeignKey("assets.id"), nullable=False, index=True)
    version_id = Column(String, ForeignKey("asset_versions.id"), nullable=False, index=True)

    # Property Info
    property_name = Column(String(100), nullable=False)  # "power", "tag", "location_id"
    property_path = Column(String(500), nullable=True)  # For nested: "specs.electrical.voltage"

    # Values
    old_value = Column(JSON, nullable=True)  # null if creation
    new_value = Column(JSON, nullable=True)  # null if deletion

    # Metadata
    changed_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    changed_by = Column(String, ForeignKey("users.id"), nullable=True)

    # Relationships
    asset = relationship("Asset", foreign_keys=[asset_id])
    version = relationship("AssetVersion", foreign_keys=[version_id])
    changer = relationship("User", foreign_keys=[changed_by])

    __table_args__ = (
        Index("ix_property_changes_asset_property", "asset_id", "property_name"),
        Index("ix_property_changes_version", "version_id"),
    )

    def __repr__(self):
        return f"<PropertyChange {self.property_name}: {self.old_value} -> {self.new_value}>"


# =============================================================================
# BATCH OPERATIONS (Group Operations for Rollback)
# =============================================================================


class BatchOperation(Base):
    """
    Groups multiple changes for bulk rollback.

    A batch operation represents a logical group of changes that should
    be rolled back together:
    - CSV import (100 assets)
    - Rule execution (creates 50 motors + 95 cables)
    - Bulk update (change discipline for 30 assets)
    """

    __tablename__ = "batch_operations"

    # Primary Key
    id = Column(String, primary_key=True, default=generate_uuid)

    # Description
    operation_type = Column(SQLEnum(BatchOperationType), nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Scope
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    affected_assets = Column(Integer, nullable=False, default=0)  # Count of assets touched

    # Timing
    started_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # User
    created_by = Column(String, ForeignKey("users.id"), nullable=True)

    # Rollback Info
    is_rolled_back = Column(Boolean, default=False, index=True)
    rolled_back_at = Column(DateTime(timezone=True), nullable=True)
    rolled_back_by = Column(String, ForeignKey("users.id"), nullable=True)
    rollback_reason = Column(Text, nullable=True)

    # Link to workflow event
    correlation_id = Column(String, nullable=False, index=True)

    # Relationships
    project = relationship("Project", foreign_keys=[project_id])
    creator = relationship("User", foreign_keys=[created_by])
    rollback_user = relationship("User", foreign_keys=[rolled_back_by])
    versions = relationship("AssetVersion", back_populates="batch")

    __table_args__ = (Index("ix_batch_operations_project_started", "project_id", "started_at"),)

    def __repr__(self):
        return f"<BatchOperation {self.operation_type.value} ({self.affected_assets} assets)>"


# =============================================================================
# ASSET CHANGES (Simple View for Quick Queries)
# =============================================================================


class AssetChange(Base):
    """
    Simple view of asset changes for quick queries.

    Links workflow events directly to specific field changes,
    enabling fast queries like "show me all changes to this asset".
    """

    __tablename__ = "asset_changes"

    # Primary Key
    id = Column(String, primary_key=True, default=generate_uuid)
    event_id = Column(String, ForeignKey("workflow_events.id"), nullable=False, index=True)
    asset_id = Column(String, ForeignKey("assets.id"), nullable=False, index=True)

    # Change Info
    field_name = Column(String(100), nullable=False)
    old_value = Column(JSON, nullable=True)
    new_value = Column(JSON, nullable=True)

    # Relationships
    event = relationship("WorkflowEvent", foreign_keys=[event_id])
    asset = relationship("Asset", foreign_keys=[asset_id])

    __table_args__ = (
        Index("ix_asset_changes_asset", "asset_id"),
        Index("ix_asset_changes_event", "event_id"),
    )

    def __repr__(self):
        return f"<AssetChange {self.field_name} on {self.asset_id}>"
