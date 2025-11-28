from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.models.auth import User
from app.models.models import LBSNode
from app.schemas.location import LBSNodeCreate, LBSNodeResponse

router = APIRouter()


@router.post("/", response_model=LBSNodeResponse)
def create_location(
    location: LBSNodeCreate,
    project_id: str = Header(..., alias="X-Project-ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_location = LBSNode(**location.model_dump(), project_id=project_id)
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location


@router.get("/", response_model=list[LBSNodeResponse])
def read_locations(
    project_id: str = Header(..., alias="X-Project-ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    locations = db.query(LBSNode).filter(LBSNode.project_id == project_id).all()
    return locations


@router.get("/{location_id}", response_model=LBSNodeResponse)
def read_location(
    location_id: str,
    project_id: str = Header(..., alias="X-Project-ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_location = (
        db.query(LBSNode)
        .filter(LBSNode.id == location_id, LBSNode.project_id == project_id)
        .first()
    )
    if db_location is None:
        raise NotFoundError("Location", location_id)
    return db_location
