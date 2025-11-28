"""
Pydantic schemas for Workflow Events, Versioning, and Traceability.

These schemas support the MVP traceability features:
- WorkflowEvent: Central event log queries and responses
- AssetVersion: Version history and snapshots
- PropertyChange: Field-level change tracking
- BatchOperation: Bulk operation management and rollback
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# =============================================================================
# ENUMS (Mirror models/workflow.py enums for API contracts)
# =============================================================================


class LogLevel(str, Enum):
    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    FATAL = "FATAL"


class LogSource(str, Enum):
    SYSTEM = "SYSTEM"
    IMPORT = "IMPORT"
    RULE = "RULE"
    PACKAGE = "PACKAGE"
    USER = "USER"
    API = "API"
    ROLLBACK = "ROLLBACK"


class WorkflowActionType(str, Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    EXECUTE = "EXECUTE"
    EXPORT = "EXPORT"
    IMPORT = "IMPORT"
    ROLLBACK = "ROLLBACK"
    VALIDATE = "VALIDATE"
    LINK = "LINK"


class WorkflowStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ROLLED_BACK = "ROLLED_BACK"


class ChangeSource(str, Enum):
    USER = "USER"
    RULE = "RULE"
    IMPORT = "IMPORT"
    API = "API"
    ROLLBACK = "ROLLBACK"
    SYSTEM = "SYSTEM"


class BatchOperationType(str, Enum):
    IMPORT = "IMPORT"
    RULE_EXECUTION = "RULE_EXECUTION"
    BULK_UPDATE = "BULK_UPDATE"
    BULK_DELETE = "BULK_DELETE"
    PACKAGE_GENERATION = "PACKAGE_GENERATION"


# =============================================================================
# WORKFLOW EVENT SCHEMAS
# =============================================================================


class WorkflowEventBase(BaseModel):
    """Base schema for workflow events"""

    level: LogLevel = LogLevel.INFO
    source: LogSource
    action_type: WorkflowActionType = Field(..., alias="actionType")
    message: str
    entity_type: str | None = Field(None, alias="entityType")
    entity_id: str | None = Field(None, alias="entityId")
    entity_tag: str | None = Field(None, alias="entityTag")
    details: dict[str, Any] | None = None
    fbs_code: str | None = Field(None, alias="fbsCode")
    lbs_code: str | None = Field(None, alias="lbsCode")
    discipline: str | None = None
    package_code: str | None = Field(None, alias="packageCode")


class WorkflowEventCreate(WorkflowEventBase):
    """Schema for creating a workflow event"""

    project_id: str = Field(..., alias="projectId")
    user_id: str | None = Field(None, alias="userId")
    session_id: str | None = Field(None, alias="sessionId")
    correlation_id: str | None = Field(None, alias="correlationId")
    parent_event_id: str | None = Field(None, alias="parentEventId")


class WorkflowEventResponse(BaseModel):
    """Schema for workflow event responses"""

    id: str
    timestamp: datetime
    level: LogLevel
    source: LogSource
    action_type: WorkflowActionType = Field(..., alias="actionType")
    status: WorkflowStatus
    project_id: str = Field(..., alias="projectId")
    user_id: str | None = Field(None, alias="userId")
    session_id: str | None = Field(None, alias="sessionId")
    entity_type: str | None = Field(None, alias="entityType")
    entity_id: str | None = Field(None, alias="entityId")
    entity_tag: str | None = Field(None, alias="entityTag")
    message: str
    details: dict[str, Any] | None = None
    parent_event_id: str | None = Field(None, alias="parentEventId")
    correlation_id: str = Field(..., alias="correlationId")
    duration_ms: int | None = Field(None, alias="durationMs")
    error: str | None = None
    fbs_code: str | None = Field(None, alias="fbsCode")
    lbs_code: str | None = Field(None, alias="lbsCode")
    discipline: str | None = None
    package_code: str | None = Field(None, alias="packageCode")

    model_config = {"from_attributes": True, "populate_by_name": True}


class WorkflowEventListResponse(BaseModel):
    """Paginated list of workflow events"""

    items: list[WorkflowEventResponse]
    total: int
    page: int
    page_size: int = Field(..., alias="pageSize")
    has_more: bool = Field(..., alias="hasMore")

    model_config = {"populate_by_name": True}


class WorkflowEventQuery(BaseModel):
    """Query parameters for filtering workflow events"""

    project_id: str = Field(..., alias="projectId")
    start_date: datetime | None = Field(None, alias="startDate")
    end_date: datetime | None = Field(None, alias="endDate")
    level: LogLevel | None = None
    source: LogSource | None = None
    action_type: WorkflowActionType | None = Field(None, alias="actionType")
    entity_type: str | None = Field(None, alias="entityType")
    entity_id: str | None = Field(None, alias="entityId")
    correlation_id: str | None = Field(None, alias="correlationId")
    session_id: str | None = Field(None, alias="sessionId")
    fbs_code: str | None = Field(None, alias="fbsCode")
    lbs_code: str | None = Field(None, alias="lbsCode")
    discipline: str | None = None
    package_code: str | None = Field(None, alias="packageCode")
    page: int = 1
    page_size: int = Field(50, alias="pageSize", ge=1, le=500)

    model_config = {"populate_by_name": True}


# =============================================================================
# ASSET VERSION SCHEMAS
# =============================================================================


class AssetVersionBase(BaseModel):
    """Base schema for asset versions"""

    version_number: int = Field(..., alias="versionNumber")
    change_reason: str | None = Field(None, alias="changeReason")
    change_source: ChangeSource = Field(..., alias="changeSource")


class AssetVersionResponse(AssetVersionBase):
    """Schema for asset version responses"""

    id: str
    asset_id: str = Field(..., alias="assetId")
    snapshot: dict[str, Any]
    created_at: datetime = Field(..., alias="createdAt")
    created_by: str | None = Field(None, alias="createdBy")
    event_id: str | None = Field(None, alias="eventId")
    batch_id: str | None = Field(None, alias="batchId")

    model_config = {"from_attributes": True, "populate_by_name": True}


class AssetVersionListResponse(BaseModel):
    """List of asset versions"""

    items: list[AssetVersionResponse]
    total: int
    asset_id: str = Field(..., alias="assetId")

    model_config = {"populate_by_name": True}


# =============================================================================
# PROPERTY CHANGE SCHEMAS
# =============================================================================


class PropertyChangeResponse(BaseModel):
    """Schema for property change responses"""

    id: str
    asset_id: str = Field(..., alias="assetId")
    version_id: str = Field(..., alias="versionId")
    property_name: str = Field(..., alias="propertyName")
    property_path: str | None = Field(None, alias="propertyPath")
    old_value: Any = Field(None, alias="oldValue")
    new_value: Any = Field(None, alias="newValue")
    changed_at: datetime = Field(..., alias="changedAt")
    changed_by: str | None = Field(None, alias="changedBy")

    model_config = {"from_attributes": True, "populate_by_name": True}


class PropertyHistoryResponse(BaseModel):
    """Timeline of changes for a specific property"""

    asset_id: str = Field(..., alias="assetId")
    property_name: str = Field(..., alias="propertyName")
    changes: list[PropertyChangeResponse]
    current_value: Any = Field(None, alias="currentValue")

    model_config = {"populate_by_name": True}


# =============================================================================
# BATCH OPERATION SCHEMAS
# =============================================================================


class BatchOperationBase(BaseModel):
    """Base schema for batch operations"""

    operation_type: BatchOperationType = Field(..., alias="operationType")
    description: str | None = None


class BatchOperationCreate(BatchOperationBase):
    """Schema for creating a batch operation"""

    project_id: str = Field(..., alias="projectId")


class BatchOperationResponse(BatchOperationBase):
    """Schema for batch operation responses"""

    id: str
    project_id: str = Field(..., alias="projectId")
    affected_assets: int = Field(..., alias="affectedAssets")
    started_at: datetime = Field(..., alias="startedAt")
    completed_at: datetime | None = Field(None, alias="completedAt")
    created_by: str | None = Field(None, alias="createdBy")
    is_rolled_back: bool = Field(..., alias="isRolledBack")
    rolled_back_at: datetime | None = Field(None, alias="rolledBackAt")
    rolled_back_by: str | None = Field(None, alias="rolledBackBy")
    rollback_reason: str | None = Field(None, alias="rollbackReason")
    correlation_id: str = Field(..., alias="correlationId")

    model_config = {"from_attributes": True, "populate_by_name": True}


class BatchOperationListResponse(BaseModel):
    """Paginated list of batch operations"""

    items: list[BatchOperationResponse]
    total: int
    page: int
    page_size: int = Field(..., alias="pageSize")
    has_more: bool = Field(..., alias="hasMore")

    model_config = {"populate_by_name": True}


# =============================================================================
# VERSION DIFF SCHEMAS
# =============================================================================


class FieldDiff(BaseModel):
    """A single field difference between versions"""

    field: str
    old_value: Any = Field(None, alias="oldValue")
    new_value: Any = Field(None, alias="newValue")

    model_config = {"populate_by_name": True}


class VersionDiffResponse(BaseModel):
    """Diff between two asset versions"""

    asset_id: str = Field(..., alias="assetId")
    from_version: int = Field(..., alias="fromVersion")
    to_version: int = Field(..., alias="toVersion")
    added: list[str] = []
    removed: list[str] = []
    modified: list[FieldDiff] = []
    unchanged_count: int = Field(0, alias="unchangedCount")

    model_config = {"populate_by_name": True}


# =============================================================================
# ROLLBACK SCHEMAS
# =============================================================================


class RollbackRequest(BaseModel):
    """Request to rollback an asset or batch"""

    reason: str | None = None


class AssetRollbackRequest(RollbackRequest):
    """Request to rollback an asset to a specific version"""

    target_version: int = Field(..., alias="targetVersion")

    model_config = {"populate_by_name": True}


class RollbackResultResponse(BaseModel):
    """Result of a rollback operation"""

    success: bool
    asset_id: str = Field(..., alias="assetId")
    from_version: int = Field(..., alias="fromVersion")
    to_version: int = Field(..., alias="toVersion")
    new_version: int = Field(..., alias="newVersion")
    message: str
    error: str | None = None

    model_config = {"populate_by_name": True}


class BatchRollbackResultResponse(BaseModel):
    """Result of a batch rollback operation"""

    success: bool
    batch_id: str = Field(..., alias="batchId")
    total_assets: int = Field(..., alias="totalAssets")
    rolled_back: int = Field(..., alias="rolledBack")
    failed: int
    results: list[RollbackResultResponse]
    message: str

    model_config = {"populate_by_name": True}


# =============================================================================
# ASSET CHANGE SCHEMAS (Quick View)
# =============================================================================


class AssetChangeResponse(BaseModel):
    """Schema for asset change quick view"""

    id: str
    event_id: str = Field(..., alias="eventId")
    asset_id: str = Field(..., alias="assetId")
    field_name: str = Field(..., alias="fieldName")
    old_value: Any = Field(None, alias="oldValue")
    new_value: Any = Field(None, alias="newValue")
    timestamp: datetime | None = None
    user_id: str | None = Field(None, alias="userId")

    model_config = {"from_attributes": True, "populate_by_name": True}


class AssetHistoryResponse(BaseModel):
    """Complete history of changes for an asset"""

    asset_id: str = Field(..., alias="assetId")
    asset_tag: str | None = Field(None, alias="assetTag")
    versions: list[AssetVersionResponse]
    changes: list[AssetChangeResponse]
    total_versions: int = Field(..., alias="totalVersions")
    total_changes: int = Field(..., alias="totalChanges")

    model_config = {"populate_by_name": True}


# =============================================================================
# TIMELINE SCHEMAS (For UI Timeline View)
# =============================================================================


class TimelineEvent(BaseModel):
    """A single event in the timeline view"""

    id: str
    timestamp: datetime
    type: str  # "event", "version", "batch"
    level: LogLevel | None = None
    source: LogSource | None = None
    action_type: WorkflowActionType | None = Field(None, alias="actionType")
    message: str
    entity_type: str | None = Field(None, alias="entityType")
    entity_id: str | None = Field(None, alias="entityId")
    entity_tag: str | None = Field(None, alias="entityTag")
    user_id: str | None = Field(None, alias="userId")
    details: dict[str, Any] | None = None
    children: list["TimelineEvent"] = []

    model_config = {"populate_by_name": True}


class TimelineResponse(BaseModel):
    """Timeline view with grouped events"""

    project_id: str = Field(..., alias="projectId")
    start_date: datetime = Field(..., alias="startDate")
    end_date: datetime = Field(..., alias="endDate")
    events: list[TimelineEvent]
    total: int

    model_config = {"populate_by_name": True}
