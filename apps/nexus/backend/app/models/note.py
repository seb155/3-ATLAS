from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import TSVECTOR
from datetime import datetime
from ..database import Base


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text)
    content_plain = Column(Text)  # Plain text for search
    parent_id = Column(Integer, ForeignKey("notes.id", ondelete="CASCADE"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    is_folder = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)  # Soft delete

    # Full-text search
    search_vector = Column(TSVECTOR)

    # Relationships
    user = relationship("User", back_populates="notes")
    parent = relationship("Note", remote_side=[id], backref="children")

    # Indexes
    __table_args__ = (
        Index('idx_notes_user', user_id),
        Index('idx_notes_parent', parent_id),
        Index('idx_notes_title', title),
        Index('idx_notes_search', search_vector, postgresql_using='gin'),
    )
