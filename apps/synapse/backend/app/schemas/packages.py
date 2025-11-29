"""
Package Schemas

Pydantic schemas for package API endpoints.
"""

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.packages import PackageStatus


class PackageBase(BaseModel):
    """Base package schema."""

    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    package_type: str | None = None
    package_metadata: dict | None = None


class PackageCreate(PackageBase):
    """Schema for creating a package."""

    status: PackageStatus | None = None


class PackageUpdate(BaseModel):
    """Schema for updating a package."""

    name: str | None = None
    description: str | None = None
    package_type: str | None = None
    package_metadata: dict | None = None
    status: PackageStatus | None = None


class PackageResponse(PackageBase):
    """Schema for package response."""

    id: str
    project_id: str
    status: PackageStatus
    created_at: datetime
    updated_at: datetime
    asset_count: int = 0

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, package):
        """Create from ORM model with asset count."""
        return cls(
            id=package.id,
            name=package.name,
            description=package.description,
            package_type=package.package_type,
            package_metadata=package.package_metadata,
            project_id=package.project_id,
            status=package.status,
            created_at=package.created_at,
            updated_at=package.updated_at,
            asset_count=len(package.assets) if package.assets else 0,
        )


class PackageListResponse(BaseModel):
    """Schema for package list response."""

    packages: list[PackageResponse]
    total: int
    page: int
    page_size: int
