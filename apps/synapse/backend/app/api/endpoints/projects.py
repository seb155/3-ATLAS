from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.models.auth import Client, Project, User
from app.models.models import Asset
from app.models.cables import Cable
from app.models.metamodel import MetamodelNode
from app.models.workflow import BatchOperation, WorkflowEvent
from app.models.action_log import ActionLog
from app.schemas.project import ClientCreate, ClientResponse, ProjectCreate, ProjectResponse

router = APIRouter()


# --- Clients ---
# --- Clients ---
@router.post("/clients", response_model=ClientResponse)
def create_client(
    client: ClientCreate,
    db: Session = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_active_user),  # noqa: B008
):
    db_client = Client(**client.model_dump())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client


@router.get("/clients", response_model=list[ClientResponse])
def get_clients(
    db: Session = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_active_user),  # noqa: B008
):
    return db.query(Client).all()


# --- Projects ---
@router.post("/projects", response_model=ProjectResponse)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_active_user),  # noqa: B008
):
    # Verify client exists
    client = db.query(Client).filter(Client.id == project.client_id).first()
    if not client:
        raise NotFoundError("Client", client.client_id)

    db_project = Project(**project.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


@router.get("/projects", response_model=list[ProjectResponse])
def get_projects(
    db: Session = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_active_user),  # noqa: B008
):
    return db.query(Project).all()


@router.get("/projects/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: str,
    db: Session = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_active_user),  # noqa: B008
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise NotFoundError("Project", project_id)
    return project


@router.delete("/projects/{project_id}")
def delete_project(
    project_id: str,
    db: Session = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_active_user),  # noqa: B008
):
    """Delete a project and all its related data (cascade delete)."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise NotFoundError("Project", project_id)

    # Cascade delete in correct FK order
    db.query(WorkflowEvent).filter(WorkflowEvent.project_id == project_id).delete()
    db.query(BatchOperation).filter(BatchOperation.project_id == project_id).delete()
    db.query(ActionLog).filter(ActionLog.project_id == project_id).delete()
    db.query(Cable).filter(Cable.project_id == project_id).delete()
    db.query(MetamodelNode).filter(MetamodelNode.project_id == project_id).delete()
    db.query(Asset).filter(Asset.project_id == project_id).delete()
    db.query(Project).filter(Project.id == project_id).delete()

    db.commit()
    return {"status": "deleted", "project_id": project_id}


@router.delete("/projects/{project_id}/assets")
def clear_project_assets(
    project_id: str,
    db: Session = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_active_user),  # noqa: B008
):
    """Clear all assets from a project (keeps project, rules, etc.)."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise NotFoundError("Project", project_id)

    # Delete related data first
    db.query(Cable).filter(Cable.project_id == project_id).delete()
    db.query(MetamodelNode).filter(MetamodelNode.project_id == project_id).delete()
    count = db.query(Asset).filter(Asset.project_id == project_id).delete()

    db.commit()
    return {"status": "cleared", "assets_deleted": count, "project_id": project_id}
