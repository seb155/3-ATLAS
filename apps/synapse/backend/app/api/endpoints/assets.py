from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.audit import log_audit
from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.models.auth import User
from app.models.models import Asset
from app.schemas.asset import AssetBulkUpdateItem, AssetCreate, AssetResponse, AssetUpdate

router = APIRouter()


@router.patch(
    "/bulk",
    response_model=list[AssetResponse],
    summary="Bulk update assets",
    description="Update multiple assets in a single request. Only provided fields are updated.",
    responses={
        200: {"description": "Assets updated successfully"},
        404: {"description": "One or more assets not found"},
    },
)
def bulk_update_assets(
    assets: list[AssetBulkUpdateItem],
    project_id: str = Header(..., alias="X-Project-ID", description="Target project ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Bulk update multiple assets with partial data."""
    updated_assets = []
    for asset_update in assets:
        db_asset = (
            db.query(Asset)
            .filter(Asset.id == asset_update.id, Asset.project_id == project_id)
            .first()
        )
        if db_asset:
            # Capture old state for diff? For now just log the update
            update_data = asset_update.model_dump(exclude_unset=True, exclude={"id"})
            for key, value in update_data.items():
                setattr(db_asset, key, value)
            updated_assets.append(db_asset)

            log_audit(db, current_user.id, "UPDATE", "ASSET", db_asset.id, {"changes": update_data})

    db.commit()
    for asset in updated_assets:
        db.refresh(asset)

    return updated_assets


@router.post(
    "/",
    response_model=AssetResponse,
    status_code=201,
    summary="Create a new asset",
    description="Creates a new asset in the specified project with full multi-tenancy isolation.",
    responses={
        201: {"description": "Asset created successfully"},
        400: {"description": "Validation error"},
        409: {"description": "Duplicate asset tag in project"},
    },
)
def create_asset(
    asset: AssetCreate,
    project_id: str = Header(..., alias="X-Project-ID", description="Target project ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new asset with validation and audit logging."""
    asset_data = asset.model_dump()
    db_asset = Asset(**asset_data, project_id=project_id)
    db.add(db_asset)

    # We flush to get the ID before logging
    db.flush()

    log_audit(db, current_user.id, "CREATE", "ASSET", db_asset.id, asset_data)

    db.commit()
    db.refresh(db_asset)
    return db_asset


@router.get(
    "/",
    response_model=list[AssetResponse],
    summary="List assets",
    description="Retrieve a paginated list of assets for the current project.",
    responses={
        200: {"description": "List of assets"},
    },
)
def read_assets(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100,
        ge=1,
        le=1000,
        description="Maximum number of records to return (max 1000)",
    ),
    project_id: str = Header(..., alias="X-Project-ID", description="Target project ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get paginated list of assets for the current project."""
    assets = (
        db.query(Asset)
        .filter(Asset.project_id == project_id)
        .filter(Asset.deleted_at.is_(None))  # Exclude soft-deleted assets
        .offset(skip)
        .limit(limit)
        .all()
    )
    return assets


@router.get(
    "/{asset_id}",
    response_model=AssetResponse,
    summary="Get asset by ID",
    description="Retrieve a specific asset by its ID.",
    responses={
        200: {"description": "Asset found"},
        404: {"description": "Asset not found"},
    },
)
def read_asset(
    asset_id: str,
    project_id: str = Header(..., alias="X-Project-ID", description="Target project ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a single asset by ID."""
    asset = (
        db.query(Asset)
        .filter(Asset.id == asset_id, Asset.project_id == project_id)
        .filter(Asset.deleted_at.is_(None))
        .first()
    )
    if asset is None:
        raise NotFoundError("Asset", asset_id)
    return asset


@router.put(
    "/{asset_id}",
    response_model=AssetResponse,
    summary="Update asset",
    description="Update an existing asset with new data.",
    responses={
        200: {"description": "Asset updated successfully"},
        404: {"description": "Asset not found"},
    },
)
def update_asset(
    asset_id: str,
    asset: AssetUpdate,
    project_id: str = Header(..., alias="X-Project-ID", description="Target project ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update an existing asset."""
    db_asset = (
        db.query(Asset)
        .filter(Asset.id == asset_id, Asset.project_id == project_id)
        .filter(Asset.deleted_at.is_(None))
        .first()
    )
    if db_asset is None:
        raise NotFoundError("Asset", asset_id)

    update_data = asset.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_asset, key, value)

    log_audit(db, current_user.id, "UPDATE", "ASSET", db_asset.id, {"changes": update_data})

    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    return db_asset
