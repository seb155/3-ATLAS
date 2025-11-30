"""
Recording model for audio files.
"""

from sqlalchemy import Column, String, Text, Float, BigInteger, DateTime, Index, Computed, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, TSVECTOR
from sqlalchemy.sql import func
import uuid
import enum
from ..database import Base


class RecordingStatus(str, enum.Enum):
    """Recording status enum."""
    RECORDING = "recording"
    COMPLETED = "completed"
    TRANSCRIBING = "transcribing"
    TRANSCRIBED = "transcribed"
    ERROR = "error"


class AudioSourceType(str, enum.Enum):
    """Audio source type enum."""
    MICROPHONE = "microphone"
    SYSTEM = "system"
    BOTH = "both"


class Recording(Base):
    """
    Recording model for audio files.

    Features:
    - UUID primary key
    - Folder organization (notes-perso, meetings)
    - Audio source tracking (mic, system, both)
    - Full-text search via PostgreSQL TSVECTOR
    - Soft delete support
    """
    __tablename__ = "recordings"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Owner (references workspace_auth.users)
    user_id = Column(UUID(as_uuid=True), nullable=False)

    # File info
    filename = Column(String(255), nullable=False)  # e.g., "2025-01-29_meeting-standup.wav"
    file_path = Column(Text, nullable=False)  # Relative path in data/
    folder = Column(String(50), nullable=False, default="notes-perso")  # 'notes-perso' | 'meetings'
    file_size_bytes = Column(BigInteger, nullable=False, default=0)
    duration_seconds = Column(Float, nullable=False, default=0)

    # Audio metadata
    sample_rate = Column(BigInteger, nullable=False, default=44100)
    channels = Column(BigInteger, nullable=False, default=2)
    format = Column(String(20), nullable=False, default="wav")
    source_type = Column(String(50), nullable=False, default=AudioSourceType.MICROPHONE.value)

    # Content metadata
    title = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)

    # Status
    status = Column(String(20), nullable=False, default=RecordingStatus.RECORDING.value)

    # Timestamps
    recorded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Soft delete

    # Full-text search (auto-computed)
    search_vector = Column(
        TSVECTOR,
        Computed("to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, ''))", persisted=True)
    )

    # Relationships
    transcription = relationship("Transcription", back_populates="recording", uselist=False, cascade="all, delete-orphan")
    tags = relationship("RecordingTag", back_populates="recording", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('idx_recordings_user_id', user_id),
        Index('idx_recordings_folder', folder),
        Index('idx_recordings_status', status),
        Index('idx_recordings_recorded_at', recorded_at),
        Index('idx_recordings_search', search_vector, postgresql_using='gin'),
        Index('idx_recordings_deleted', deleted_at, postgresql_where=deleted_at.is_(None)),
    )

    def __repr__(self):
        return f"<Recording(id={self.id}, filename='{self.filename}')>"

    @property
    def is_deleted(self) -> bool:
        """Check if recording is soft-deleted."""
        return self.deleted_at is not None
