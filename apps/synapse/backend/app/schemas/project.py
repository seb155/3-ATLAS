from datetime import datetime

from pydantic import BaseModel


class ProjectBase(BaseModel):
    name: str
    description: str | None = None
    status: str = "ACTIVE"


class ProjectCreate(ProjectBase):
    client_id: str


class ProjectUpdate(ProjectBase):
    name: str | None = None
    client_id: str | None = None


class ProjectResponse(ProjectBase):
    id: str
    client_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class ClientBase(BaseModel):
    name: str
    contact_email: str | None = None


class ClientCreate(ClientBase):
    pass


class ClientResponse(ClientBase):
    id: str
    projects: list[ProjectResponse] = []

    class Config:
        from_attributes = True
