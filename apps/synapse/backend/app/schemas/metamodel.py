from typing import Any

from pydantic import BaseModel

from app.models.metamodel import DisciplineType, SemanticType


class NodeCreate(BaseModel):
    name: str
    type: str  # Legacy Type
    discipline: DisciplineType = DisciplineType.GENERAL
    semantic_type: SemanticType = SemanticType.ASSET
    lod: int = 2
    isa95_level: int = 0
    description: str | None = None
    properties: dict[str, Any] | None = {}
    project_id: str | None = None


class NodeRead(NodeCreate):
    id: str
    model_config = {"from_attributes": True}


class EdgeCreate(BaseModel):
    source_node_id: str
    target_node_id: str
    relation_type: str
    cardinality: str = "1:N"
    discipline: DisciplineType = DisciplineType.GENERAL
    properties: dict[str, Any] = {}


class EdgeRead(EdgeCreate):
    id: str
    model_config = {"from_attributes": True}


class GraphRead(BaseModel):
    nodes: list[NodeRead]
    edges: list[EdgeRead]
