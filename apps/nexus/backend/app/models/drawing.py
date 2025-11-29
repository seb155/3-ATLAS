"""
Drawing model for Excalidraw integration.

Features:
- Excalidraw elements stored as JSONB
- Hierarchical structure (folders)
- Full-text search via PostgreSQL TSVECTOR
- Soft delete support
- Optimistic locking via version field
- Auto-generated thumbnails (base64 PNG)
"""

from sqlalchemy import Column, String, Text, Boolean, Integer, DateTime, ForeignKey, Index, Computed, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func
import uuid
from ..database import Base


class Drawing(Base):
    """
    Drawing model for Excalidraw canvases.

    Stores Excalidraw data as JSONB for efficient querying and storage.
    Supports hierarchical organization via parent_id (folders).
    """
    __tablename__ = "drawings"

    # Primary key (UUID for consistency)
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Metadata
    title = Column(String(500), nullable=False)
    description = Column(Text, default="")

    # Excalidraw data (JSONB for efficient storage and querying)
    elements = Column(JSONB, nullable=False, default=list)  # Excalidraw elements array
    app_state = Column(JSONB, default=dict)  # Excalidraw appState (zoom, background, etc.)
    files = Column(JSONB, default=dict)  # Embedded images/files as base64

    # Thumbnail for preview (base64 PNG, generated client-side)
    thumbnail = Column(Text, nullable=True)

    # Optimistic locking
    version = Column(Integer, nullable=False, default=1)

    # Owner (references workspace_auth.users via UUID)
    user_id = Column(UUID(as_uuid=True), nullable=False)

    # Hierarchy (folders)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("drawings.id", ondelete="CASCADE"), nullable=True)
    is_folder = Column(Boolean, default=False)

    # Timestamps (timezone-aware)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Soft delete

    # Full-text search (auto-computed from title + description)
    content_tsvector = Column(
        "content_tsvector",
        Computed("to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, ''))", persisted=True)
    )

    # Self-referential relationship for hierarchy
    parent = relationship("Drawing", remote_side=[id], backref="children")

    # Indexes
    __table_args__ = (
        Index('idx_drawings_user_id', user_id),
        Index('idx_drawings_parent_id', parent_id),
        Index('idx_drawings_title', title),
        Index('idx_drawings_content_tsvector', 'content_tsvector', postgresql_using='gin'),
        Index('idx_drawings_deleted_at', deleted_at, postgresql_where=deleted_at.is_(None)),
    )

    def __repr__(self):
        title_preview = self.title[:30] if self.title else "Untitled"
        return f"<Drawing(id={self.id}, title='{title_preview}')>"

    @property
    def is_deleted(self) -> bool:
        """Check if drawing is soft-deleted."""
        return self.deleted_at is not None

    @property
    def is_root(self) -> bool:
        """Check if drawing is a root-level drawing (no parent)."""
        return self.parent_id is None


class NoteDrawingEmbed(Base):
    """
    Association table tracking drawings embedded in notes.

    Links drawings to notes when inserted as TipTap blocks.
    Stores display settings for each embed instance.
    """
    __tablename__ = "note_drawing_embeds"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # References
    note_id = Column(UUID(as_uuid=True), ForeignKey("notes.id", ondelete="CASCADE"), nullable=False)
    drawing_id = Column(UUID(as_uuid=True), ForeignKey("drawings.id", ondelete="CASCADE"), nullable=False)

    # Display settings
    edit_mode = Column(
        String(10),
        nullable=False,
        default='modal'
    )
    width = Column(Integer, default=800)
    height = Column(Integer, default=400)

    # Position in note (for ordering multiple embeds)
    position = Column(Integer, default=0)

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Constraints
    __table_args__ = (
        Index('idx_note_drawing_embeds_note', note_id),
        Index('idx_note_drawing_embeds_drawing', drawing_id),
        CheckConstraint("edit_mode IN ('modal', 'inline')", name='chk_edit_mode'),
    )
