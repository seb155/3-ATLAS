"""
Notes API Router with CRUD, search, backlinks, and tree operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from ..database import get_db
from ..schemas.note import (
    Note, NoteCreate, NoteUpdate, NoteWithBacklinks,
    SearchResponse, NoteTreeResponse, NoteTreeItem
)
from ..services.notes import NotesService
from ..utils.dependencies import get_current_user
from ..models.user import User

router = APIRouter(prefix="/notes", tags=["notes"])


# ============================================================================
# CRUD Operations
# ============================================================================

@router.post("", response_model=Note, status_code=status.HTTP_201_CREATED)
def create_note(
    note: NoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new note."""
    return NotesService.create_note(db, note, current_user.id)


@router.get("", response_model=List[Note])
def get_notes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    parent_id: Optional[UUID] = Query(None, description="Filter by parent note"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all notes for the current user, optionally filtered by parent."""
    return NotesService.get_notes(db, current_user.id, skip, limit, parent_id)


@router.get("/root", response_model=List[Note])
def get_root_notes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get root-level notes (notes without a parent)."""
    return NotesService.get_root_notes(db, current_user.id)


@router.get("/tree", response_model=NoteTreeResponse)
def get_note_tree(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the complete note tree structure for building a sidebar tree view."""
    tree = NotesService.get_note_tree(db, current_user.id)
    return NoteTreeResponse(
        notes=[NoteTreeItem(**item) for item in tree],
        total=len(tree)
    )


@router.get("/search", response_model=SearchResponse)
def search_notes(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Full-text search across notes using PostgreSQL TSVECTOR."""
    results = NotesService.search_notes(db, current_user.id, q, limit)
    return SearchResponse(
        query=q,
        total=len(results),
        results=results
    )


@router.get("/{note_id}", response_model=Note)
def get_note(
    note_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a single note by ID."""
    note = NotesService.get_note(db, note_id, current_user.id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.get("/{note_id}/backlinks", response_model=NoteWithBacklinks)
def get_note_with_backlinks(
    note_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a note with all its backlinks (notes that link to it via [[wiki-links]])."""
    note = NotesService.get_note(db, note_id, current_user.id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    backlinks = NotesService.get_backlinks(db, note_id, current_user.id)

    # Convert Note to dict and add backlinks
    note_data = {
        "id": note.id,
        "title": note.title,
        "content": note.content,
        "content_plain": note.content_plain,
        "parent_id": note.parent_id,
        "user_id": note.user_id,
        "is_folder": note.is_folder,
        "created_at": note.created_at,
        "updated_at": note.updated_at,
        "deleted_at": note.deleted_at,
        "backlinks": backlinks
    }

    return NoteWithBacklinks(**note_data)


@router.get("/{note_id}/children", response_model=List[Note])
def get_note_children(
    note_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all child notes of a specific note."""
    # First verify the parent note exists and belongs to user
    parent = NotesService.get_note(db, note_id, current_user.id)
    if not parent:
        raise HTTPException(status_code=404, detail="Parent note not found")

    return NotesService.get_notes(db, current_user.id, parent_id=note_id)


@router.put("/{note_id}", response_model=Note)
def update_note(
    note_id: UUID,
    note_update: NoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an existing note."""
    note = NotesService.update_note(db, note_id, current_user.id, note_update)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.put("/{note_id}/move", response_model=Note)
def move_note(
    note_id: UUID,
    new_parent_id: Optional[UUID] = Query(None, description="New parent ID, or null for root"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Move a note to a new parent in the hierarchy."""
    note = NotesService.move_note(db, note_id, current_user.id, new_parent_id)
    if not note:
        raise HTTPException(
            status_code=400,
            detail="Cannot move note. Parent not found or would create a cycle."
        )
    return note


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    note_id: UUID,
    hard: bool = Query(False, description="Permanently delete instead of soft delete"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a note (soft delete by default)."""
    if not NotesService.delete_note(db, note_id, current_user.id, hard_delete=hard):
        raise HTTPException(status_code=404, detail="Note not found")
