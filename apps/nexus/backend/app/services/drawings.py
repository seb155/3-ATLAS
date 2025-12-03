"""
Drawings service with CRUD, search, and backlinks functionality.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, text
from ..models.drawing import Drawing, NoteDrawingEmbed
from ..models.note import Note
from ..schemas.drawing import (
    DrawingCreate, DrawingUpdate, DrawingSearchResult, BacklinkInfo,
    NoteDrawingEmbedCreate
)
from typing import List, Optional
from uuid import UUID
from datetime import datetime


class DrawingsService:
    """Service for managing drawings."""

    @staticmethod
    def create_drawing(db: Session, drawing: DrawingCreate, user_id: UUID) -> Drawing:
        """Create a new drawing."""
        db_drawing = Drawing(
            title=drawing.title,
            description=drawing.description,
            elements=drawing.elements,
            app_state=drawing.app_state,
            files=drawing.files,
            parent_id=drawing.parent_id,
            is_folder=drawing.is_folder,
            user_id=user_id
        )
        db.add(db_drawing)
        db.commit()
        db.refresh(db_drawing)
        return db_drawing

    @staticmethod
    def get_drawings(
        db: Session,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
        parent_id: Optional[UUID] = None,
        include_deleted: bool = False
    ) -> List[Drawing]:
        """Get drawings for a user, optionally filtered by parent."""
        query = db.query(Drawing).filter(Drawing.user_id == user_id)

        if not include_deleted:
            query = query.filter(Drawing.deleted_at.is_(None))

        if parent_id is not None:
            query = query.filter(Drawing.parent_id == parent_id)

        return query.order_by(Drawing.is_folder.desc(), Drawing.title).offset(skip).limit(limit).all()

    @staticmethod
    def get_root_drawings(db: Session, user_id: UUID) -> List[Drawing]:
        """Get root-level drawings (no parent)."""
        return db.query(Drawing).filter(
            Drawing.user_id == user_id,
            Drawing.parent_id.is_(None),
            Drawing.deleted_at.is_(None)
        ).order_by(Drawing.is_folder.desc(), Drawing.title).all()

    @staticmethod
    def get_drawing(db: Session, drawing_id: UUID, user_id: UUID) -> Drawing | None:
        """Get a single drawing by ID."""
        return db.query(Drawing).filter(
            Drawing.id == drawing_id,
            Drawing.user_id == user_id,
            Drawing.deleted_at.is_(None)
        ).first()

    @staticmethod
    def update_drawing(
        db: Session,
        drawing_id: UUID,
        user_id: UUID,
        drawing_update: DrawingUpdate
    ) -> Drawing | None:
        """Update an existing drawing with optimistic locking."""
        db_drawing = DrawingsService.get_drawing(db, drawing_id, user_id)
        if not db_drawing:
            return None

        # Check version for optimistic locking
        if db_drawing.version != drawing_update.version:
            raise ValueError("Drawing was modified by another session")

        update_data = drawing_update.model_dump(exclude_unset=True, exclude={"version"})

        for field, value in update_data.items():
            setattr(db_drawing, field, value)

        # Increment version
        db_drawing.version += 1

        db.commit()
        db.refresh(db_drawing)
        return db_drawing

    @staticmethod
    def delete_drawing(db: Session, drawing_id: UUID, user_id: UUID, hard_delete: bool = False) -> bool:
        """Delete a drawing (soft delete by default)."""
        db_drawing = DrawingsService.get_drawing(db, drawing_id, user_id)
        if not db_drawing:
            return False

        if hard_delete:
            db.delete(db_drawing)
        else:
            db_drawing.deleted_at = datetime.utcnow()

        db.commit()
        return True

    @staticmethod
    def search_drawings(
        db: Session,
        user_id: UUID,
        query: str,
        limit: int = 20
    ) -> List[DrawingSearchResult]:
        """Full-text search across drawings using PostgreSQL TSVECTOR."""
        if not query or len(query.strip()) < 2:
            return []

        # Use PostgreSQL full-text search
        search_query = func.plainto_tsquery('english', query)

        results = db.query(
            Drawing.id,
            Drawing.title,
            Drawing.description,
            Drawing.thumbnail,
            Drawing.is_folder,
            func.ts_rank(Drawing.content_tsvector, search_query).label('score')
        ).filter(
            Drawing.user_id == user_id,
            Drawing.deleted_at.is_(None),
            Drawing.content_tsvector.op('@@')(search_query)
        ).order_by(
            text('score DESC')
        ).limit(limit).all()

        return [
            DrawingSearchResult(
                id=r.id,
                title=r.title,
                description=r.description or "",
                thumbnail=r.thumbnail,
                score=float(r.score) if r.score else 0.0,
                is_folder=r.is_folder
            )
            for r in results
        ]

    @staticmethod
    def get_drawing_tree(db: Session, user_id: UUID) -> List[dict]:
        """Get the complete drawing tree structure for a user."""
        drawings = db.query(
            Drawing.id,
            Drawing.title,
            Drawing.parent_id,
            Drawing.is_folder,
            Drawing.thumbnail
        ).filter(
            Drawing.user_id == user_id,
            Drawing.deleted_at.is_(None)
        ).order_by(Drawing.is_folder.desc(), Drawing.title).all()

        # Count children for each drawing
        children_counts = {}
        for d in drawings:
            if d.parent_id:
                children_counts[d.parent_id] = children_counts.get(d.parent_id, 0) + 1

        return [
            {
                "id": d.id,
                "title": d.title,
                "parent_id": d.parent_id,
                "is_folder": d.is_folder,
                "children_count": children_counts.get(d.id, 0),
                "thumbnail": d.thumbnail
            }
            for d in drawings
        ]

    @staticmethod
    def find_drawing_by_title(db: Session, user_id: UUID, title: str) -> Drawing | None:
        """Find a drawing by its exact title."""
        return db.query(Drawing).filter(
            Drawing.user_id == user_id,
            Drawing.title == title,
            Drawing.deleted_at.is_(None)
        ).first()

    @staticmethod
    def move_drawing(db: Session, drawing_id: UUID, user_id: UUID, new_parent_id: Optional[UUID]) -> Drawing | None:
        """Move a drawing to a new parent (or to root if new_parent_id is None)."""
        drawing = DrawingsService.get_drawing(db, drawing_id, user_id)
        if not drawing:
            return None

        # Validate new parent exists and belongs to user
        if new_parent_id:
            new_parent = DrawingsService.get_drawing(db, new_parent_id, user_id)
            if not new_parent:
                return None
            # Prevent moving a drawing into itself or its descendants
            if DrawingsService._is_descendant(db, new_parent_id, drawing_id):
                return None

        drawing.parent_id = new_parent_id
        db.commit()
        db.refresh(drawing)
        return drawing

    @staticmethod
    def _is_descendant(db: Session, potential_descendant_id: UUID, ancestor_id: UUID) -> bool:
        """Check if potential_descendant is a descendant of ancestor."""
        current = db.query(Drawing).filter(Drawing.id == potential_descendant_id).first()
        while current:
            if current.id == ancestor_id:
                return True
            if current.parent_id is None:
                return False
            current = db.query(Drawing).filter(Drawing.id == current.parent_id).first()
        return False

    @staticmethod
    def update_thumbnail(db: Session, drawing_id: UUID, user_id: UUID, thumbnail: str) -> bool:
        """Update drawing thumbnail."""
        db_drawing = DrawingsService.get_drawing(db, drawing_id, user_id)
        if not db_drawing:
            return False

        db_drawing.thumbnail = thumbnail
        db.commit()
        return True

    @staticmethod
    def get_backlinks(db: Session, drawing_id: UUID, user_id: UUID) -> List[BacklinkInfo]:
        """Get all notes/drawings that embed or link to the specified drawing."""
        backlinks = []

        # Get notes that embed this drawing
        embeds = db.query(
            Note.id,
            Note.title,
            NoteDrawingEmbed.created_at
        ).join(
            NoteDrawingEmbed, NoteDrawingEmbed.note_id == Note.id
        ).filter(
            NoteDrawingEmbed.drawing_id == drawing_id,
            Note.user_id == user_id,
            Note.deleted_at.is_(None)
        ).all()

        for e in embeds:
            backlinks.append(BacklinkInfo(
                id=e.id,
                title=e.title,
                type="note",
                link_text=None,
                created_at=e.created_at
            ))

        return backlinks

    # ============================================================================
    # Note-Drawing Embed Operations
    # ============================================================================

    @staticmethod
    def create_embed(db: Session, embed: NoteDrawingEmbedCreate) -> NoteDrawingEmbed:
        """Create a note-drawing embed relationship."""
        db_embed = NoteDrawingEmbed(
            note_id=embed.note_id,
            drawing_id=embed.drawing_id,
            edit_mode=embed.edit_mode,
            width=embed.width,
            height=embed.height,
            position=embed.position
        )
        db.add(db_embed)
        db.commit()
        db.refresh(db_embed)
        return db_embed

    @staticmethod
    def get_embeds_for_note(db: Session, note_id: UUID) -> List[NoteDrawingEmbed]:
        """Get all drawing embeds for a note."""
        return db.query(NoteDrawingEmbed).filter(
            NoteDrawingEmbed.note_id == note_id
        ).order_by(NoteDrawingEmbed.position).all()

    @staticmethod
    def delete_embed(db: Session, embed_id: UUID) -> bool:
        """Delete a note-drawing embed."""
        db_embed = db.query(NoteDrawingEmbed).filter(
            NoteDrawingEmbed.id == embed_id
        ).first()
        if not db_embed:
            return False

        db.delete(db_embed)
        db.commit()
        return True

    @staticmethod
    def get_drawings_for_note(db: Session, note_id: UUID, user_id: UUID) -> List[Drawing]:
        """Get all drawings embedded in a note."""
        return db.query(Drawing).join(
            NoteDrawingEmbed, NoteDrawingEmbed.drawing_id == Drawing.id
        ).filter(
            NoteDrawingEmbed.note_id == note_id,
            Drawing.user_id == user_id,
            Drawing.deleted_at.is_(None)
        ).all()
