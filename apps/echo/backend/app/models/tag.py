"""
Tag models for recording categorization.
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from ..database import Base


class Tag(Base):
    """Tag model for categorizing recordings."""
    __tablename__ = "tags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    name = Column(String(100), nullable=False)
    color = Column(String(7), default="#6366f1")  # Hex color
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    recordings = relationship("RecordingTag", back_populates="tag", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_tags_user_id', user_id),
        Index('idx_tags_name', name),
    )

    def __repr__(self):
        return f"<Tag(id={self.id}, name='{self.name}')>"


class RecordingTag(Base):
    """Association table for recordings and tags."""
    __tablename__ = "recording_tags"

    recording_id = Column(UUID(as_uuid=True), ForeignKey("recordings.id", ondelete="CASCADE"), primary_key=True)
    tag_id = Column(UUID(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    recording = relationship("Recording", back_populates="tags")
    tag = relationship("Tag", back_populates="recordings")

    __table_args__ = (
        Index('idx_recording_tags_recording', recording_id),
        Index('idx_recording_tags_tag', tag_id),
    )
