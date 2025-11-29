"""
Package Management & Export API Endpoints

Provides endpoints for:
- Package CRUD operations
- Package asset management
- Template-based export (IN-P040, CA-P040)
- Export history tracking
"""

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Response
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.models.auth import User
from app.models.models import Asset
from app.models.packages import Package, PackageStatus
from app.schemas.packages import (
    PackageCreate,
    PackageListResponse,
    PackageResponse,
    PackageUpdate,
)
from app.services.template_service import TemplateService

router = APIRouter()


# =============================================================================
# PACKAGE CRUD ENDPOINTS
# =============================================================================


@router.get(
    "",
    response_model=PackageListResponse,
    summary="List packages",
    description="Get all packages for a project",
)
def list_packages(
    project_id: str = Header(..., alias="X-Project-ID"),
    status: PackageStatus | None = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List all packages for a project."""
    query = db.query(Package).filter(Package.project_id == project_id)

    if status:
        query = query.filter(Package.status == status)

    total = query.count()
    packages = query.offset((page - 1) * page_size).limit(page_size).all()

    return PackageListResponse(
        packages=[PackageResponse.from_orm(p) for p in packages],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post(
    "",
    response_model=PackageResponse,
    status_code=201,
    summary="Create package",
    description="Create a new package",
)
def create_package(
    package_data: PackageCreate,
    project_id: str = Header(..., alias="X-Project-ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new package."""
    package = Package(
        name=package_data.name,
        description=package_data.description,
        package_type=package_data.package_type,
        package_metadata=package_data.package_metadata,
        project_id=project_id,
        status=package_data.status or PackageStatus.OPEN,
    )

    db.add(package)
    db.commit()
    db.refresh(package)

    return PackageResponse.from_orm(package)


@router.get(
    "/{package_id}",
    response_model=PackageResponse,
    summary="Get package",
    description="Get package details with asset count",
)
def get_package(
    package_id: str,
    project_id: str = Header(..., alias="X-Project-ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get package by ID."""
    package = (
        db.query(Package)
        .filter(Package.id == package_id, Package.project_id == project_id)
        .first()
    )

    if not package:
        raise HTTPException(status_code=404, detail="Package not found")

    return PackageResponse.from_orm(package)


@router.patch(
    "/{package_id}",
    response_model=PackageResponse,
    summary="Update package",
    description="Update package details",
)
def update_package(
    package_id: str,
    package_data: PackageUpdate,
    project_id: str = Header(..., alias="X-Project-ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update package."""
    package = (
        db.query(Package)
        .filter(Package.id == package_id, Package.project_id == project_id)
        .first()
    )

    if not package:
        raise HTTPException(status_code=404, detail="Package not found")

    # Update fields
    if package_data.name is not None:
        package.name = package_data.name
    if package_data.description is not None:
        package.description = package_data.description
    if package_data.status is not None:
        package.status = package_data.status

    db.commit()
    db.refresh(package)

    return PackageResponse.from_orm(package)


@router.delete(
    "/{package_id}",
    status_code=204,
    summary="Delete package",
    description="Delete a package (must be empty)",
)
def delete_package(
    package_id: str,
    project_id: str = Header(..., alias="X-Project-ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete package (only if empty)."""
    package = (
        db.query(Package)
        .filter(Package.id == package_id, Package.project_id == project_id)
        .first()
    )

    if not package:
        raise HTTPException(status_code=404, detail="Package not found")

    # Check if package has assets
    asset_count = db.query(Asset).filter(Asset.package_id == package_id).count()
    if asset_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete package with {asset_count} assets. Remove assets first.",
        )

    db.delete(package)
    db.commit()

    return Response(status_code=204)


# =============================================================================
# PACKAGE ASSET MANAGEMENT
# =============================================================================


@router.get(
    "/{package_id}/assets",
    summary="Get package assets",
    description="List all assets in a package",
)
def get_package_assets(
    package_id: str,
    project_id: str = Header(..., alias="X-Project-ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get all assets in a package."""
    package = (
        db.query(Package)
        .filter(Package.id == package_id, Package.project_id == project_id)
        .first()
    )

    if not package:
        raise HTTPException(status_code=404, detail="Package not found")

    assets = (
        db.query(Asset).filter(Asset.package_id == package_id).order_by(Asset.tag).all()
    )

    return {
        "package_id": package_id,
        "package_name": package.name,
        "asset_count": len(assets),
        "assets": [
            {
                "id": a.id,
                "tag": a.tag,
                "asset_type": a.type,
                "description": (a.properties or {}).get("description", ""),
            }
            for a in assets
        ],
    }


@router.post(
    "/{package_id}/assets/{asset_id}",
    status_code=204,
    summary="Add asset to package",
    description="Assign an asset to this package",
)
def add_asset_to_package(
    package_id: str,
    asset_id: str,
    project_id: str = Header(..., alias="X-Project-ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Add an asset to a package."""
    # Verify package exists
    package = (
        db.query(Package)
        .filter(Package.id == package_id, Package.project_id == project_id)
        .first()
    )
    if not package:
        raise HTTPException(status_code=404, detail="Package not found")

    # Get asset
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    # Assign package
    asset.package_id = package_id
    db.commit()

    return Response(status_code=204)


@router.delete(
    "/{package_id}/assets/{asset_id}",
    status_code=204,
    summary="Remove asset from package",
    description="Unassign an asset from this package",
)
def remove_asset_from_package(
    package_id: str,
    asset_id: str,
    project_id: str = Header(..., alias="X-Project-ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Remove an asset from a package."""
    asset = db.query(Asset).filter(Asset.id == asset_id, Asset.package_id == package_id).first()

    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found in this package")

    asset.package_id = None
    db.commit()

    return Response(status_code=204)


# =============================================================================
# TEMPLATE EXPORT ENDPOINTS
# =============================================================================


@router.get(
    "/{package_id}/export",
    summary="Export package",
    description="Export package using specified template (IN-P040, CA-P040)",
)
def export_package(
    package_id: str,
    template_type: str = Query(
        ..., description="Template type (IN-P040, CA-P040)", regex="^(IN-P040|CA-P040)$"
    ),
    format: str = Query("xlsx", description="Export format (xlsx, pdf)", regex="^(xlsx|pdf)$"),
    project_id: str = Header(..., alias="X-Project-ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Export package to Excel/PDF using template.

    Templates:
    - IN-P040: Instrument Index
    - CA-P040: Cable Schedule
    """
    # Verify package exists
    package = (
        db.query(Package)
        .filter(Package.id == package_id, Package.project_id == project_id)
        .first()
    )
    if not package:
        raise HTTPException(status_code=404, detail="Package not found")

    # Initialize template service
    template_service = TemplateService(db)

    # Export
    result = template_service.export_package(
        package_id=package_id, template_type=template_type, format=format
    )

    if not result.success:
        raise HTTPException(status_code=500, detail=result.error)

    # Return file
    return Response(
        content=result.file_data,
        media_type=result.mime_type,
        headers={
            "Content-Disposition": f'attachment; filename="{result.file_name}"',
            "Content-Type": result.mime_type,
        },
    )


@router.get(
    "/{package_id}/export/preview",
    summary="Preview export data",
    description="Preview the data that would be exported (for debugging)",
)
def preview_export_data(
    package_id: str,
    template_type: str = Query(..., description="Template type", regex="^(IN-P040|CA-P040)$"),
    project_id: str = Header(..., alias="X-Project-ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Preview export data without generating file."""
    package = (
        db.query(Package)
        .filter(Package.id == package_id, Package.project_id == project_id)
        .first()
    )
    if not package:
        raise HTTPException(status_code=404, detail="Package not found")

    assets = (
        db.query(Asset).filter(Asset.package_id == package_id).order_by(Asset.tag).all()
    )

    preview_data = {
        "package": {
            "id": package.id,
            "name": package.name,
            "status": package.status,
        },
        "template_type": template_type,
        "asset_count": len(assets),
        "assets": [
            {
                "tag": a.tag,
                "type": a.type,
                "properties": a.properties,
            }
            for a in assets[:10]  # Limit to 10 for preview
        ],
    }

    if template_type == "CA-P040":
        # Include cable count
        from app.models.cables import Cable

        asset_ids = [a.id for a in assets]
        cable_count = (
            db.query(Cable)
            .filter(Cable.from_asset_id.in_(asset_ids), Cable.to_asset_id.in_(asset_ids))
            .count()
        )
        preview_data["cable_count"] = cable_count

    return preview_data
