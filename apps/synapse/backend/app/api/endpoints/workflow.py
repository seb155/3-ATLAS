"""
Workflow Traceability API Endpoints

Provides endpoints for:
- Workflow Events: Query event log, timeline view
- Asset Versions: Version history, diffs, rollback
- Batch Operations: Bulk operation management and rollback
- Property Changes: Field-level change history

Central to MVP demo: "Je peux voir exactement ce qui se passe"
"""

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.models.auth import User
from app.models.workflow import (
    AssetChange,
    AssetVersion,
    BatchOperation,
    PropertyChange,
    WorkflowEvent,
)
from app.schemas.workflow import (
    AssetChangeResponse,
    AssetHistoryResponse,
    AssetRollbackRequest,
    AssetVersionListResponse,
    AssetVersionResponse,
    BatchOperationListResponse,
    BatchOperationResponse,
    BatchRollbackResultResponse,
    FieldDiff,
    PropertyChangeResponse,
    PropertyHistoryResponse,
    RollbackResultResponse,
    TimelineEvent,
    TimelineResponse,
    VersionDiffResponse,
    WorkflowEventListResponse,
    WorkflowEventResponse,
)
from app.services.versioning_service import VersioningService

router = APIRouter()


# =============================================================================
# WORKFLOW EVENTS ENDPOINTS
# =============================================================================


@router.get(
    "/events",
    response_model=WorkflowEventListResponse,
    summary="Query workflow events",
    description="Retrieve paginated workflow events with filtering",
)
def get_workflow_events(
    project_id: str = Header(..., alias="X-Project-ID"),
    start_date: datetime | None = Query(None, description="Filter from date"),
    end_date: datetime | None = Query(None, description="Filter to date"),
    level: str | None = Query(None, description="Filter by log level"),
    source: str | None = Query(None, description="Filter by event source"),
    action_type: str | None = Query(None, description="Filter by action type"),
    entity_type: str | None = Query(None, description="Filter by entity type"),
    entity_id: str | None = Query(None, description="Filter by entity ID"),
    correlation_id: str | None = Query(None, description="Filter by correlation ID"),
    session_id: str | None = Query(None, description="Filter by session ID"),
    fbs_code: str | None = Query(None, description="Filter by FBS code"),
    lbs_code: str | None = Query(None, description="Filter by LBS code"),
    discipline: str | None = Query(None, description="Filter by discipline"),
    package_code: str | None = Query(None, description="Filter by package code"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Query workflow events with comprehensive filtering."""
    query = db.query(WorkflowEvent).filter(WorkflowEvent.project_id == project_id)

    if start_date:
        query = query.filter(WorkflowEvent.timestamp >= start_date)
    if end_date:
        query = query.filter(WorkflowEvent.timestamp <= end_date)
    if level:
        query = query.filter(WorkflowEvent.level == level)
    if source:
        query = query.filter(WorkflowEvent.source == source)
    if action_type:
        query = query.filter(WorkflowEvent.action_type == action_type)
    if entity_type:
        query = query.filter(WorkflowEvent.entity_type == entity_type)
    if entity_id:
        query = query.filter(WorkflowEvent.entity_id == entity_id)
    if correlation_id:
        query = query.filter(WorkflowEvent.correlation_id == correlation_id)
    if session_id:
        query = query.filter(WorkflowEvent.session_id == session_id)
    if fbs_code:
        query = query.filter(WorkflowEvent.fbs_code == fbs_code)
    if lbs_code:
        query = query.filter(WorkflowEvent.lbs_code == lbs_code)
    if discipline:
        query = query.filter(WorkflowEvent.discipline == discipline)
    if package_code:
        query = query.filter(WorkflowEvent.package_code == package_code)

    total = query.count()
    events = (
        query.order_by(desc(WorkflowEvent.timestamp))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return WorkflowEventListResponse(
        items=[WorkflowEventResponse.model_validate(e) for e in events],
        total=total,
        page=page,
        page_size=page_size,
        has_more=(page * page_size) < total,
    )


@router.get(
    "/events/{event_id}",
    response_model=WorkflowEventResponse,
    summary="Get single workflow event",
)
def get_workflow_event(
    event_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a single workflow event by ID."""
    event = db.query(WorkflowEvent).filter(WorkflowEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Workflow event not found")
    return WorkflowEventResponse.model_validate(event)


@router.get(
    "/events/correlation/{correlation_id}",
    response_model=list[WorkflowEventResponse],
    summary="Get events by correlation ID",
    description="Get all events that share the same correlation ID",
)
def get_events_by_correlation(
    correlation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get all events with a specific correlation ID."""
    events = (
        db.query(WorkflowEvent)
        .filter(WorkflowEvent.correlation_id == correlation_id)
        .order_by(WorkflowEvent.timestamp)
        .all()
    )
    return [WorkflowEventResponse.model_validate(e) for e in events]


# =============================================================================
# TIMELINE ENDPOINT
# =============================================================================


@router.get(
    "/timeline",
    response_model=TimelineResponse,
    summary="Get timeline view",
    description="Get a timeline of events for visualization",
)
def get_timeline(
    project_id: str = Header(..., alias="X-Project-ID"),
    hours: int = Query(24, ge=1, le=168, description="Hours of history to show"),
    entity_id: str | None = Query(None, description="Filter by entity ID"),
    correlation_id: str | None = Query(None, description="Filter by correlation ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get timeline view of workflow events."""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(hours=hours)

    query = db.query(WorkflowEvent).filter(
        WorkflowEvent.project_id == project_id,
        WorkflowEvent.timestamp >= start_date,
        WorkflowEvent.timestamp <= end_date,
    )

    if entity_id:
        query = query.filter(WorkflowEvent.entity_id == entity_id)
    if correlation_id:
        query = query.filter(WorkflowEvent.correlation_id == correlation_id)

    events = query.order_by(desc(WorkflowEvent.timestamp)).limit(500).all()

    timeline_events = []
    for e in events:
        timeline_events.append(
            TimelineEvent(
                id=e.id,
                timestamp=e.timestamp,
                type="event",
                level=e.level,
                source=e.source,
                action_type=e.action_type,
                message=e.message,
                entity_type=e.entity_type,
                entity_id=e.entity_id,
                entity_tag=e.entity_tag,
                user_id=e.user_id,
                details=e.details,
                children=[],
            )
        )

    return TimelineResponse(
        project_id=project_id,
        start_date=start_date,
        end_date=end_date,
        events=timeline_events,
        total=len(timeline_events),
    )


# =============================================================================
# ASSET VERSION ENDPOINTS
# =============================================================================


@router.get(
    "/assets/{asset_id}/versions",
    response_model=AssetVersionListResponse,
    summary="Get asset version history",
)
def get_asset_versions(
    asset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get all versions of an asset."""
    versions = (
        db.query(AssetVersion)
        .filter(AssetVersion.asset_id == asset_id)
        .order_by(desc(AssetVersion.version_number))
        .all()
    )

    return AssetVersionListResponse(
        items=[AssetVersionResponse.model_validate(v) for v in versions],
        total=len(versions),
        asset_id=asset_id,
    )


@router.get(
    "/assets/{asset_id}/versions/{version_number}",
    response_model=AssetVersionResponse,
    summary="Get specific asset version",
)
def get_asset_version(
    asset_id: str,
    version_number: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific version of an asset."""
    version = (
        db.query(AssetVersion)
        .filter(
            AssetVersion.asset_id == asset_id,
            AssetVersion.version_number == version_number,
        )
        .first()
    )
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    return AssetVersionResponse.model_validate(version)


@router.get(
    "/assets/{asset_id}/diff",
    response_model=VersionDiffResponse,
    summary="Diff between two versions",
)
def diff_asset_versions(
    asset_id: str,
    from_version: int = Query(..., description="Version to compare from"),
    to_version: int = Query(..., description="Version to compare to"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get diff between two asset versions."""
    versioning_service = VersioningService(db)

    try:
        diff = versioning_service.diff_versions(asset_id, from_version, to_version)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return VersionDiffResponse(
        asset_id=asset_id,
        from_version=from_version,
        to_version=to_version,
        added=diff.added,
        removed=diff.removed,
        modified=[
            FieldDiff(field=m["field"], old_value=m["old_value"], new_value=m["new_value"])
            for m in diff.modified
        ],
        unchanged_count=diff.unchanged_count,
    )


@router.post(
    "/assets/{asset_id}/rollback",
    response_model=RollbackResultResponse,
    summary="Rollback asset to version",
)
def rollback_asset(
    asset_id: str,
    request: AssetRollbackRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Rollback an asset to a specific version."""
    versioning_service = VersioningService(db)

    try:
        result = versioning_service.rollback_asset_to_version(
            asset_id=asset_id,
            target_version=request.target_version,
            user_id=current_user.id,
            reason=request.reason,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return RollbackResultResponse(
        success=result.success,
        asset_id=result.asset_id,
        from_version=result.from_version,
        to_version=result.to_version,
        new_version=result.new_version,
        message=result.message,
        error=result.error,
    )


# =============================================================================
# ASSET HISTORY ENDPOINT
# =============================================================================


@router.get(
    "/assets/{asset_id}/history",
    response_model=AssetHistoryResponse,
    summary="Get complete asset history",
    description="Get versions and changes for an asset",
)
def get_asset_history(
    asset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get complete history of an asset."""
    versions = (
        db.query(AssetVersion)
        .filter(AssetVersion.asset_id == asset_id)
        .order_by(desc(AssetVersion.version_number))
        .all()
    )

    changes = (
        db.query(AssetChange)
        .filter(AssetChange.asset_id == asset_id)
        .order_by(desc(AssetChange.id))
        .all()
    )

    asset_tag = None
    if versions:
        snapshot = versions[0].snapshot
        if isinstance(snapshot, dict):
            asset_tag = snapshot.get("tag")

    return AssetHistoryResponse(
        asset_id=asset_id,
        asset_tag=asset_tag,
        versions=[AssetVersionResponse.model_validate(v) for v in versions],
        changes=[AssetChangeResponse.model_validate(c) for c in changes],
        total_versions=len(versions),
        total_changes=len(changes),
    )


# =============================================================================
# PROPERTY HISTORY ENDPOINT
# =============================================================================


@router.get(
    "/assets/{asset_id}/properties/{property_name}/history",
    response_model=PropertyHistoryResponse,
    summary="Get property change history",
)
def get_property_history(
    asset_id: str,
    property_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get history of changes for a specific property."""
    changes = (
        db.query(PropertyChange)
        .filter(
            PropertyChange.asset_id == asset_id,
            PropertyChange.property_name == property_name,
        )
        .order_by(desc(PropertyChange.changed_at))
        .all()
    )

    current_value = None
    if changes:
        current_value = changes[0].new_value

    return PropertyHistoryResponse(
        asset_id=asset_id,
        property_name=property_name,
        changes=[PropertyChangeResponse.model_validate(c) for c in changes],
        current_value=current_value,
    )


# =============================================================================
# BATCH OPERATIONS ENDPOINTS
# =============================================================================


@router.get(
    "/batches",
    response_model=BatchOperationListResponse,
    summary="List batch operations",
)
def get_batch_operations(
    project_id: str = Header(..., alias="X-Project-ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    include_rolled_back: bool = Query(False, description="Include rolled back batches"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List batch operations for a project."""
    query = db.query(BatchOperation).filter(BatchOperation.project_id == project_id)

    if not include_rolled_back:
        query = query.filter(BatchOperation.is_rolled_back is False)

    total = query.count()
    batches = (
        query.order_by(desc(BatchOperation.started_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return BatchOperationListResponse(
        items=[BatchOperationResponse.model_validate(b) for b in batches],
        total=total,
        page=page,
        page_size=page_size,
        has_more=(page * page_size) < total,
    )


@router.get(
    "/batches/{batch_id}",
    response_model=BatchOperationResponse,
    summary="Get batch operation",
)
def get_batch_operation(
    batch_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a batch operation by ID."""
    batch = db.query(BatchOperation).filter(BatchOperation.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch operation not found")
    return BatchOperationResponse.model_validate(batch)


@router.post(
    "/batches/{batch_id}/rollback",
    response_model=BatchRollbackResultResponse,
    summary="Rollback batch operation",
)
def rollback_batch(
    batch_id: str,
    reason: str = Query(None, description="Reason for rollback"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Rollback an entire batch operation."""
    versioning_service = VersioningService(db)

    try:
        result = versioning_service.rollback_batch(
            batch_id=batch_id,
            user_id=current_user.id,
            reason=reason,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return BatchRollbackResultResponse(
        success=result.success,
        batch_id=result.batch_id,
        total_assets=result.total_assets,
        rolled_back=result.rolled_back,
        failed=result.failed,
        results=[
            RollbackResultResponse(
                success=r.success,
                asset_id=r.asset_id,
                from_version=r.from_version,
                to_version=r.to_version,
                new_version=r.new_version,
                message=r.message,
                error=r.error,
            )
            for r in result.results
        ],
        message=result.message,
    )


# =============================================================================
# STATS ENDPOINT
# =============================================================================


@router.get(
    "/stats",
    summary="Get workflow statistics",
    description="Get summary statistics for workflow events",
)
def get_workflow_stats(
    project_id: str = Header(..., alias="X-Project-ID"),
    hours: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get workflow statistics for dashboard."""
    cutoff = datetime.utcnow() - timedelta(hours=hours)

    total_events = (
        db.query(func.count(WorkflowEvent.id))
        .filter(
            WorkflowEvent.project_id == project_id,
            WorkflowEvent.timestamp >= cutoff,
        )
        .scalar()
    )

    events_by_source = (
        db.query(WorkflowEvent.source, func.count(WorkflowEvent.id))
        .filter(
            WorkflowEvent.project_id == project_id,
            WorkflowEvent.timestamp >= cutoff,
        )
        .group_by(WorkflowEvent.source)
        .all()
    )

    events_by_action = (
        db.query(WorkflowEvent.action_type, func.count(WorkflowEvent.id))
        .filter(
            WorkflowEvent.project_id == project_id,
            WorkflowEvent.timestamp >= cutoff,
        )
        .group_by(WorkflowEvent.action_type)
        .all()
    )

    error_count = (
        db.query(func.count(WorkflowEvent.id))
        .filter(
            WorkflowEvent.project_id == project_id,
            WorkflowEvent.timestamp >= cutoff,
            WorkflowEvent.level.in_(["ERROR", "FATAL"]),
        )
        .scalar()
    )

    return {
        "period_hours": hours,
        "total_events": total_events,
        "error_count": error_count,
        "by_source": {str(s.value): c for s, c in events_by_source},
        "by_action": {str(a.value): c for a, c in events_by_action},
    }
