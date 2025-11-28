from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.auth import User
from app.models.cables import Cable

router = APIRouter()


@router.get("/", response_model=list[dict])
def list_cables(
    project_id: UUID = Header(..., alias="X-Project-ID"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List cables for a project.
    """
    cables = (
        db.query(Cable)
        .filter(
            Cable.project_id == str(project_id)  # Convert UUID to string
        )
        .offset(skip)
        .limit(limit)
        .all()
    )

    # Simple serialization for now, can be improved with Pydantic schemas later
    return [
        {
            "id": str(c.id),
            "tag": c.tag,
            "type": "CABLE",  # For frontend compatibility
            "project_id": str(c.project_id),
            "properties": c.properties,
            "area": c.to_asset.area if c.to_asset else None,
            "system": c.to_asset.system if c.to_asset else None,
            "description": c.description,
            "cable_type": c.cable_type,
            "conductor_size": c.conductor_size,
            "length_meters": c.length_meters,
            "voltage_drop_percent": c.voltage_drop_percent,
        }
        for c in cables
    ]


@router.get("/{cable_id}", response_model=dict)
def get_cable(
    cable_id: UUID,
    project_id: UUID = Header(..., alias="X-Project-ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a specific cable.
    """
    cable = (
        db.query(Cable)
        .filter(Cable.id == str(cable_id), Cable.project_id == str(project_id))
        .first()
    )

    if not cable:
        raise HTTPException(status_code=404, detail="Cable not found")

    return {
        "id": str(cable.id),
        "tag": cable.tag,
        "type": "CABLE",
        "project_id": str(cable.project_id),
        "properties": cable.properties,
        "area": cable.to_asset.area if cable.to_asset else None,
        "system": cable.to_asset.system if cable.to_asset else None,
        "description": cable.description,
        "cable_type": cable.cable_type,
        "conductor_size": cable.conductor_size,
        "length_meters": cable.length_meters,
        "voltage_drop_percent": cable.voltage_drop_percent,
    }
