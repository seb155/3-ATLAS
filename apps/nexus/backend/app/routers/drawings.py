"""
Drawings API Router with CRUD, search, backlinks, and tree operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from ..database import get_db
from ..schemas.drawing import (
    Drawing, DrawingCreate, DrawingUpdate, DrawingWithBacklinks,
    DrawingSearchResponse, DrawingTreeResponse, DrawingTreeItem,
    ThumbnailUpdate, DrawingMove, NoteDrawingEmbed, NoteDrawingEmbedCreate,
    DiagramGenerateRequest, DiagramGenerateResponse
)
from ..services.drawings import DrawingsService
from ..utils.dependencies import get_current_user
from ..models.user import User

router = APIRouter(prefix="/drawings", tags=["drawings"])


# ============================================================================
# CRUD Operations
# ============================================================================

@router.post("", response_model=Drawing, status_code=status.HTTP_201_CREATED)
def create_drawing(
    drawing: DrawingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new drawing."""
    return DrawingsService.create_drawing(db, drawing, current_user.id)


@router.get("", response_model=List[Drawing])
def get_drawings(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    parent_id: Optional[UUID] = Query(None, description="Filter by parent drawing/folder"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all drawings for the current user, optionally filtered by parent."""
    return DrawingsService.get_drawings(db, current_user.id, skip, limit, parent_id)


@router.get("/root", response_model=List[Drawing])
def get_root_drawings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get root-level drawings (drawings without a parent)."""
    return DrawingsService.get_root_drawings(db, current_user.id)


@router.get("/tree", response_model=DrawingTreeResponse)
def get_drawing_tree(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the complete drawing tree structure for building a sidebar tree view."""
    tree = DrawingsService.get_drawing_tree(db, current_user.id)
    return DrawingTreeResponse(
        drawings=[DrawingTreeItem(**item) for item in tree],
        total=len(tree)
    )


@router.get("/search", response_model=DrawingSearchResponse)
def search_drawings(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Full-text search across drawings using PostgreSQL TSVECTOR."""
    results = DrawingsService.search_drawings(db, current_user.id, q, limit)
    return DrawingSearchResponse(
        query=q,
        total=len(results),
        results=results
    )


@router.get("/find", response_model=Optional[Drawing])
def find_drawing_by_title(
    title: str = Query(..., description="Drawing title to find"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Find a drawing by its exact title (for wiki-link resolution)."""
    drawing = DrawingsService.find_drawing_by_title(db, current_user.id, title)
    if not drawing:
        return None
    return drawing


@router.get("/{drawing_id}", response_model=Drawing)
def get_drawing(
    drawing_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a single drawing by ID."""
    drawing = DrawingsService.get_drawing(db, drawing_id, current_user.id)
    if not drawing:
        raise HTTPException(status_code=404, detail="Drawing not found")
    return drawing


@router.get("/{drawing_id}/backlinks", response_model=DrawingWithBacklinks)
def get_drawing_with_backlinks(
    drawing_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a drawing with all its backlinks (notes that embed it)."""
    drawing = DrawingsService.get_drawing(db, drawing_id, current_user.id)
    if not drawing:
        raise HTTPException(status_code=404, detail="Drawing not found")

    backlinks = DrawingsService.get_backlinks(db, drawing_id, current_user.id)

    # Convert Drawing to dict and add backlinks
    drawing_data = {
        "id": drawing.id,
        "title": drawing.title,
        "description": drawing.description,
        "elements": drawing.elements,
        "app_state": drawing.app_state,
        "files": drawing.files,
        "thumbnail": drawing.thumbnail,
        "version": drawing.version,
        "parent_id": drawing.parent_id,
        "user_id": drawing.user_id,
        "is_folder": drawing.is_folder,
        "created_at": drawing.created_at,
        "updated_at": drawing.updated_at,
        "deleted_at": drawing.deleted_at,
        "backlinks": backlinks
    }

    return DrawingWithBacklinks(**drawing_data)


@router.put("/{drawing_id}", response_model=Drawing)
def update_drawing(
    drawing_id: UUID,
    drawing_update: DrawingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an existing drawing (requires version for optimistic locking)."""
    try:
        drawing = DrawingsService.update_drawing(db, drawing_id, current_user.id, drawing_update)
        if not drawing:
            raise HTTPException(status_code=404, detail="Drawing not found")
        return drawing
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.put("/{drawing_id}/move", response_model=Drawing)
def move_drawing(
    drawing_id: UUID,
    move: DrawingMove,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Move a drawing to a new parent in the hierarchy."""
    drawing = DrawingsService.move_drawing(db, drawing_id, current_user.id, move.new_parent_id)
    if not drawing:
        raise HTTPException(
            status_code=400,
            detail="Cannot move drawing. Parent not found or would create a cycle."
        )
    return drawing


@router.put("/{drawing_id}/thumbnail", status_code=status.HTTP_204_NO_CONTENT)
def update_thumbnail(
    drawing_id: UUID,
    thumbnail_update: ThumbnailUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update drawing thumbnail (base64 PNG)."""
    if not DrawingsService.update_thumbnail(db, drawing_id, current_user.id, thumbnail_update.thumbnail):
        raise HTTPException(status_code=404, detail="Drawing not found")


@router.delete("/{drawing_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_drawing(
    drawing_id: UUID,
    hard: bool = Query(False, description="Permanently delete instead of soft delete"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a drawing (soft delete by default)."""
    if not DrawingsService.delete_drawing(db, drawing_id, current_user.id, hard_delete=hard):
        raise HTTPException(status_code=404, detail="Drawing not found")


# ============================================================================
# Note-Drawing Embed Operations
# ============================================================================

@router.post("/embeds", response_model=NoteDrawingEmbed, status_code=status.HTTP_201_CREATED)
def create_embed(
    embed: NoteDrawingEmbedCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a note-drawing embed relationship."""
    # Verify drawing belongs to user
    drawing = DrawingsService.get_drawing(db, embed.drawing_id, current_user.id)
    if not drawing:
        raise HTTPException(status_code=404, detail="Drawing not found")

    return DrawingsService.create_embed(db, embed)


@router.get("/embeds/note/{note_id}", response_model=List[NoteDrawingEmbed])
def get_embeds_for_note(
    note_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all drawing embeds for a note."""
    return DrawingsService.get_embeds_for_note(db, note_id)


@router.delete("/embeds/{embed_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_embed(
    embed_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a note-drawing embed."""
    if not DrawingsService.delete_embed(db, embed_id):
        raise HTTPException(status_code=404, detail="Embed not found")


# ============================================================================
# AI Generation (Phase 6 Placeholder)
# ============================================================================

@router.post("/generate", response_model=DiagramGenerateResponse)
def generate_diagram(
    request: DiagramGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate diagram from text description using AI (Phase 6).

    Currently returns 501 Not Implemented.
    """
    raise HTTPException(
        status_code=501,
        detail="AI diagram generation is planned for Phase 6. Stay tuned!"
    )
