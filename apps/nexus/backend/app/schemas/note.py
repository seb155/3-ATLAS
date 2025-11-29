"""
Pydantic schemas for Notes API.

All IDs are UUID strings for consistency with the database schema.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from uuid import UUID


class NoteBase(BaseModel):
    """Base schema for note data."""
    title: str = Field(..., min_length=1, max_length=500)
    content: Optional[str] = Field(default="", description="Rich HTML content")
    parent_id: Optional[UUID] = Field(default=None, description="Parent note UUID for hierarchy")
    is_folder: bool = Field(default=False, description="True if this is a folder/container")


class NoteCreate(NoteBase):
    """Schema for creating a new note."""
    pass


class NoteUpdate(BaseModel):
    """Schema for updating an existing note. All fields optional."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=500)
    content: Optional[str] = None
    parent_id: Optional[UUID] = None
    is_folder: Optional[bool] = None


class Note(NoteBase):
    """Schema for note response."""
    id: UUID
    user_id: UUID
    content_plain: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class NoteTreeItem(BaseModel):
    """Compact note representation for tree view."""
    id: UUID
    title: str
    parent_id: Optional[UUID] = None
    is_folder: bool = False
    children_count: int = 0

    class Config:
        from_attributes = True


class BacklinkInfo(BaseModel):
    """Information about a note that links to another note."""
    id: UUID
    title: str
    link_text: Optional[str] = None
    created_at: datetime


class NoteWithBacklinks(Note):
    """Note with its backlinks (notes that link to it)."""
    backlinks: List[BacklinkInfo] = []


class SearchResult(BaseModel):
    """Search result item."""
    id: UUID
    title: str
    snippet: str = ""  # Highlighted snippet from content
    score: float = 0.0
    is_folder: bool = False

    class Config:
        from_attributes = True


class SearchResponse(BaseModel):
    """Search endpoint response."""
    query: str
    total: int
    results: List[SearchResult]


class NoteTreeResponse(BaseModel):
    """Response for note tree structure."""
    notes: List[NoteTreeItem]
    total: int
