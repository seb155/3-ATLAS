from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.models.auth import Client, Project, User
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
