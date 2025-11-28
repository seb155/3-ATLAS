"""
Validation API Endpoints

Endpoints for validating assets against engineering rules.
"""


from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.database import get_db
from app.services.validation_service import ValidationService

router = APIRouter()


class ValidationResponse(BaseModel):
    """Response schema for validation results"""

    total_assets: int
    validation_results: list[dict]
    summary: dict

    model_config = {"serialize_by_alias": True}


@router.post("/assets/{asset_id}/validate")
def validate_asset(
    asset_id: str,
    project_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> ValidationResponse:
    """
    Validate a single asset against all applicable VALIDATE rules.

    Args:
        asset_id: Asset ID to validate
        project_id: Project ID from X-Project-ID header
        db: Database session
        current_user: Authenticated user

    Returns:
        ValidationResponse with results and summary
    """
    results = ValidationService.validate_asset(db, asset_id, project_id)
    summary = ValidationService.get_validation_summary(results)

    return ValidationResponse(
        total_assets=1, validation_results=[r.to_dict() for r in results], summary=summary
    )


@router.post("/projects/{project_id}/validate")
def validate_project(
    project_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)
) -> ValidationResponse:
    """
    Validate all assets in a project against applicable VALIDATE rules.

    Args:
        project_id: Project ID to validate
        db: Database session
        current_user: Authenticated user

    Returns:
        ValidationResponse with results and summary
    """
    # Verify user has access to project
    # (This is implicitly checked by require_project_access in get_current_user)

    results = ValidationService.validate_project(db, project_id)
    summary = ValidationService.get_validation_summary(results)

    return ValidationResponse(
        total_assets=summary.get("assets_validated", 0),
        validation_results=[r.to_dict() for r in results],
        summary=summary,
    )
