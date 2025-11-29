"""
Trilium Sync API Router - Bidirectional synchronization with TriliumNext.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from pydantic import BaseModel

from ..database import get_db
from ..services.trilium_sync import TriliumSyncService, TriliumAPIError
from ..utils.dependencies import get_current_user
from ..models.user import User
from ..config import get_settings

router = APIRouter(prefix="/trilium", tags=["trilium"])


# ============================================================================
# Response Models
# ============================================================================

class TriliumStatus(BaseModel):
    """Trilium connection status."""
    configured: bool
    connected: bool
    app_version: Optional[str] = None
    error: Optional[str] = None


class SyncStats(BaseModel):
    """Sync operation statistics."""
    imported: int
    skipped: int
    errors: int


class FullSyncStats(BaseModel):
    """Full bidirectional sync statistics."""
    pulled: int
    pushed: int
    conflicts: int
    errors: int


class TriliumNote(BaseModel):
    """Trilium note representation."""
    note_id: str
    title: str
    type: str
    mime: Optional[str] = None
    is_protected: bool
    children_count: int


# ============================================================================
# Connection & Status
# ============================================================================

@router.get("/status", response_model=TriliumStatus)
async def get_trilium_status(
    current_user: User = Depends(get_current_user)
):
    """Check Trilium connection status."""
    service = TriliumSyncService()

    if not service.is_configured:
        return TriliumStatus(
            configured=False,
            connected=False,
            error="Trilium ETAPI URL and token not configured"
        )

    try:
        async with service:
            app_info = await service.get_app_info()
            return TriliumStatus(
                configured=True,
                connected=True,
                app_version=app_info.get("appVersion")
            )
    except TriliumAPIError as e:
        return TriliumStatus(
            configured=True,
            connected=False,
            error=e.message
        )
    except Exception as e:
        return TriliumStatus(
            configured=True,
            connected=False,
            error=str(e)
        )


# ============================================================================
# Browse Trilium Notes
# ============================================================================

@router.get("/notes/{note_id}", response_model=TriliumNote)
async def get_trilium_note(
    note_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get a note from Trilium by ID."""
    service = TriliumSyncService()

    if not service.is_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Trilium not configured"
        )

    try:
        async with service:
            note = await service.get_note(note_id)
            return TriliumNote(
                note_id=note["noteId"],
                title=note.get("title", "Untitled"),
                type=note.get("type", "text"),
                mime=note.get("mime"),
                is_protected=note.get("isProtected", False),
                children_count=len(note.get("childNoteIds", []))
            )
    except TriliumAPIError as e:
        raise HTTPException(status_code=e.status, detail=e.message)


@router.get("/notes", response_model=list[TriliumNote])
async def search_trilium_notes(
    search: str = Query("*", description="Search query"),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user)
):
    """Search notes in Trilium."""
    service = TriliumSyncService()

    if not service.is_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Trilium not configured"
        )

    try:
        async with service:
            notes = await service.search_notes(search, limit)
            return [
                TriliumNote(
                    note_id=note["noteId"],
                    title=note.get("title", "Untitled"),
                    type=note.get("type", "text"),
                    mime=note.get("mime"),
                    is_protected=note.get("isProtected", False),
                    children_count=len(note.get("childNoteIds", []))
                )
                for note in notes
            ]
    except TriliumAPIError as e:
        raise HTTPException(status_code=e.status, detail=e.message)


# ============================================================================
# Sync Operations
# ============================================================================

@router.post("/sync/import", response_model=SyncStats)
async def import_from_trilium(
    start_note_id: str = Query("root", description="Trilium note ID to start import from"),
    recursive: bool = Query(True, description="Import child notes recursively"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Import notes from Trilium into NEXUS.

    - Starts from specified note (default: root)
    - Creates NEXUS notes with sync mapping
    - Skips system notes (starting with _) and protected notes
    """
    service = TriliumSyncService()

    if not service.is_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Trilium not configured"
        )

    try:
        async with service:
            stats = await service.import_from_trilium(
                db=db,
                user_id=current_user.id,
                trilium_note_id=start_note_id,
                recursive=recursive
            )
            return SyncStats(**stats)
    except TriliumAPIError as e:
        raise HTTPException(status_code=e.status, detail=e.message)


@router.post("/sync/push/{note_id}")
async def push_to_trilium(
    note_id: UUID,
    parent_trilium_id: str = Query("root", description="Parent note ID in Trilium"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Push a NEXUS note to Trilium.

    - Creates new note in Trilium if not already synced
    - Updates existing Trilium note if already synced
    """
    service = TriliumSyncService()

    if not service.is_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Trilium not configured"
        )

    try:
        async with service:
            trilium_id = await service.push_to_trilium(
                db=db,
                nexus_note_id=note_id,
                parent_trilium_id=parent_trilium_id
            )

            if trilium_id:
                return {
                    "status": "success",
                    "trilium_note_id": trilium_id
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Note not found"
                )
    except TriliumAPIError as e:
        raise HTTPException(status_code=e.status, detail=e.message)


@router.post("/sync/full", response_model=FullSyncStats)
async def full_sync(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Perform full bidirectional sync.

    1. Pulls new/updated notes from Trilium
    2. Pushes pending NEXUS changes to Trilium
    """
    service = TriliumSyncService()

    if not service.is_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Trilium not configured"
        )

    try:
        async with service:
            stats = await service.sync_all(db=db, user_id=current_user.id)
            return FullSyncStats(**stats)
    except TriliumAPIError as e:
        raise HTTPException(status_code=e.status, detail=e.message)


# ============================================================================
# Sync Status
# ============================================================================

@router.get("/sync/status/{note_id}")
def get_note_sync_status(
    note_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get sync status for a specific NEXUS note."""
    service = TriliumSyncService()
    sync_info = service.get_sync_status(db, note_id)

    if not sync_info:
        return {
            "synced": False,
            "trilium_note_id": None,
            "sync_status": None,
            "last_synced_at": None
        }

    return {
        "synced": True,
        "trilium_note_id": sync_info.trilium_note_id,
        "sync_status": sync_info.sync_status,
        "last_synced_at": sync_info.last_synced_at,
        "source": sync_info.source
    }
