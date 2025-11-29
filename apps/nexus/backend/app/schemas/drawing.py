"""
Pydantic schemas for Drawings API (Excalidraw integration).

All IDs are UUID strings for consistency with the database schema.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Any, Literal
from uuid import UUID


class DrawingBase(BaseModel):
    """Base schema for drawing data."""
    title: str = Field(..., min_length=1, max_length=500)
    description: str = Field(default="", max_length=5000)
    parent_id: Optional[UUID] = Field(default=None, description="Parent drawing/folder UUID for hierarchy")
    is_folder: bool = Field(default=False, description="True if this is a folder/container")


class DrawingCreate(DrawingBase):
    """Schema for creating a new drawing."""
    elements: List[Any] = Field(default_factory=list, description="Excalidraw elements array")
    app_state: dict = Field(default_factory=dict, description="Excalidraw appState (zoom, background, etc.)")
    files: dict = Field(default_factory=dict, description="Embedded images/files as base64")


class DrawingUpdate(BaseModel):
    """Schema for updating an existing drawing. All fields optional except version."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=500)
    description: Optional[str] = Field(default=None, max_length=5000)
    elements: Optional[List[Any]] = None
    app_state: Optional[dict] = None
    files: Optional[dict] = None
    parent_id: Optional[UUID] = None
    version: int = Field(..., description="Current version for optimistic locking")


class Drawing(DrawingBase):
    """Schema for drawing response."""
    id: UUID
    user_id: UUID
    elements: List[Any]
    app_state: dict
    files: dict
    thumbnail: Optional[str] = None
    version: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DrawingTreeItem(BaseModel):
    """Compact drawing representation for tree view."""
    id: UUID
    title: str
    parent_id: Optional[UUID] = None
    is_folder: bool = False
    children_count: int = 0
    thumbnail: Optional[str] = None

    class Config:
        from_attributes = True


class DrawingTreeResponse(BaseModel):
    """Response for drawing tree structure."""
    drawings: List[DrawingTreeItem]
    total: int


class DrawingSearchResult(BaseModel):
    """Search result item for drawings."""
    id: UUID
    title: str
    description: str = ""
    thumbnail: Optional[str] = None
    score: float = 0.0
    is_folder: bool = False

    class Config:
        from_attributes = True


class DrawingSearchResponse(BaseModel):
    """Search endpoint response for drawings."""
    query: str
    total: int
    results: List[DrawingSearchResult]


class BacklinkInfo(BaseModel):
    """Information about a note/drawing that links to a drawing."""
    id: UUID
    title: str
    type: Literal["note", "drawing"]
    link_text: Optional[str] = None
    created_at: datetime


class DrawingWithBacklinks(Drawing):
    """Drawing with its backlinks."""
    backlinks: List[BacklinkInfo] = []


class ThumbnailUpdate(BaseModel):
    """Schema for updating drawing thumbnail."""
    thumbnail: str = Field(..., description="Base64 encoded PNG thumbnail")


class DrawingMove(BaseModel):
    """Schema for moving a drawing to new parent."""
    new_parent_id: Optional[UUID] = Field(default=None, description="New parent ID, or null for root")


# Embed schemas
class NoteDrawingEmbedCreate(BaseModel):
    """Schema for creating a note-drawing embed."""
    note_id: UUID
    drawing_id: UUID
    edit_mode: Literal["modal", "inline"] = "modal"
    width: int = Field(default=800, ge=200, le=2000)
    height: int = Field(default=400, ge=100, le=1500)
    position: int = Field(default=0, ge=0)


class NoteDrawingEmbed(NoteDrawingEmbedCreate):
    """Schema for note-drawing embed response."""
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# AI Generation schemas (Phase 6 placeholder)
class DiagramGenerateRequest(BaseModel):
    """Schema for AI diagram generation request."""
    description: str = Field(..., min_length=10, max_length=5000, description="Text description of the diagram")
    diagram_type: Literal["architecture", "flowchart", "mindmap", "wireframe", "sequence", "erd"] = Field(
        ..., description="Type of diagram to generate"
    )
    style: Optional[str] = Field(default="default", description="Visual style (default, minimal, colorful)")


class DiagramGenerateResponse(BaseModel):
    """Schema for AI diagram generation response."""
    status: Literal["success", "pending", "error"]
    drawing_id: Optional[UUID] = None
    message: str
