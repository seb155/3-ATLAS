"""
TriliumSync model for mapping NEXUS notes to TriliumNext notes.
Enables bidirectional synchronization between the two systems.
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Index, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from ..database import Base


class TriliumSync(Base):
    """
    Mapping table between NEXUS notes and TriliumNext notes.
    
    Enables:
    - Bidirectional sync between NEXUS and TriliumNext
    - Conflict detection via UTC timestamps
    - Tracking of sync status
    """
    __tablename__ = "trilium_sync"

    # NEXUS note reference (primary key)
    nexus_note_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("notes.id", ondelete="CASCADE"),
        primary_key=True
    )

    # Trilium note ID (12-character alphanumeric)
    trilium_note_id = Column(String(12), unique=True, nullable=False, index=True)

    # Last successful sync timestamp
    last_synced_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Trilium's UTC modification timestamp (milliseconds since epoch)
    # Used for conflict detection
    trilium_utc_modified = Column(BigInteger, nullable=True)

    # Sync status
    # synced: Both systems in sync
    # pending_push: NEXUS changes need to be pushed to Trilium
    # pending_pull: Trilium changes need to be pulled to NEXUS
    # conflict: Both systems have changes (manual resolution required)
    sync_status = Column(
        String(20), 
        default="synced", 
        nullable=False,
        index=True
    )

    # Source system that created this note
    # nexus: Note was created in NEXUS, synced to Trilium
    # trilium: Note was imported from Trilium
    source = Column(String(10), default="trilium", nullable=False)

    # Trilium note metadata (cached for performance)
    trilium_type = Column(String(20), nullable=True)  # text, code, image, etc.
    trilium_mime = Column(String(50), nullable=True)  # text/html, text/markdown, etc.

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        Index('idx_trilium_sync_status', sync_status),
        Index('idx_trilium_sync_source', source),
    )

    def __repr__(self):
        return f"<TriliumSync(nexus={self.nexus_note_id}, trilium={self.trilium_note_id}, status={self.sync_status})>"
