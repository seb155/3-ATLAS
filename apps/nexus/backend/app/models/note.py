from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Index, Computed
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import TSVECTOR, UUID
from sqlalchemy.sql import func
import uuid
from ..database import Base


class Note(Base):
    """
    Note model for the Notes/Wiki system.

    Features:
    - Hierarchical structure (parent-child relationships)
    - Full-text search via PostgreSQL TSVECTOR (auto-computed)
    - Soft delete support
    - Rich content (HTML) with plain text extraction
    - Wiki-style links support
    """
    __tablename__ = "notes"

    # Primary key (UUID for consistency with User model)
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Content
    title = Column(String(500), nullable=False)
    content = Column(Text, default="")  # Rich HTML content
    content_plain = Column(Text, default="")  # Plain text for search

    # Hierarchy
    parent_id = Column(UUID(as_uuid=True), ForeignKey("notes.id", ondelete="CASCADE"), nullable=True)

    # Owner (references workspace_auth.users via UUID)
    user_id = Column(UUID(as_uuid=True), nullable=False)

    # Flags
    is_folder = Column(Boolean, default=False)

    # Timestamps (timezone-aware)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Soft delete

    # Full-text search (auto-computed from title + content_plain)
    content_tsvector = Column(
        TSVECTOR,
        Computed("to_tsvector('english', coalesce(title, '') || ' ' || coalesce(content_plain, ''))", persisted=True)
    )

    # Self-referential relationship for hierarchy
    parent = relationship("Note", remote_side=[id], backref="children")

    # Indexes (matching existing database schema)
    __table_args__ = (
        Index('idx_notes_user_id', user_id),
        Index('idx_notes_parent_id', parent_id),
        Index('idx_notes_title', title),
        Index('idx_notes_content_tsvector', content_tsvector, postgresql_using='gin'),
        Index('idx_notes_deleted_at', deleted_at, postgresql_where=deleted_at.is_(None)),
    )

    def __repr__(self):
        title_preview = self.title[:30] if self.title else "Untitled"
        return f"<Note(id={self.id}, title='{title_preview}')>"

    @property
    def is_deleted(self) -> bool:
        """Check if note is soft-deleted."""
        return self.deleted_at is not None

    @property
    def is_root(self) -> bool:
        """Check if note is a root-level note (no parent)."""
        return self.parent_id is None


class Tag(Base):
    """Tag model for categorizing notes."""
    __tablename__ = "tags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    name = Column(String(100), nullable=False)
    color = Column(String(7), default="#6366f1")  # Hex color
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index('idx_tags_user_id', user_id),
        Index('idx_tags_name', name),
    )


class NoteTag(Base):
    """Association table for notes and tags."""
    __tablename__ = "note_tags"

    note_id = Column(UUID(as_uuid=True), ForeignKey("notes.id", ondelete="CASCADE"), primary_key=True)
    tag_id = Column(UUID(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index('idx_note_tags_note', note_id),
        Index('idx_note_tags_tag', tag_id),
    )


class WikiLink(Base):
    """Wiki-style links between notes ([[note-name]] syntax)."""
    __tablename__ = "wiki_links"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_note_id = Column(UUID(as_uuid=True), ForeignKey("notes.id", ondelete="CASCADE"), nullable=False)
    target_note_id = Column(UUID(as_uuid=True), ForeignKey("notes.id", ondelete="CASCADE"), nullable=False)
    link_text = Column(String(255), nullable=True)  # The text used in [[link_text]]
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    source_note = relationship("Note", foreign_keys=[source_note_id], backref="outgoing_links")
    target_note = relationship("Note", foreign_keys=[target_note_id], backref="incoming_links")

    __table_args__ = (
        Index('idx_wiki_links_source', source_note_id),
        Index('idx_wiki_links_target', target_note_id),
    )
