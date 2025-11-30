"""
Transcription models for speech-to-text.
"""

from sqlalchemy import Column, String, Text, Float, Integer, DateTime, ForeignKey, Index, Computed, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, TSVECTOR, JSONB
from sqlalchemy.sql import func
import uuid
import enum
from ..database import Base


class TranscriptionStatus(str, enum.Enum):
    """Transcription status enum."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


class Transcription(Base):
    """
    Transcription model for speech-to-text results.

    Features:
    - Links to Recording
    - Language detection (FR-CA, EN)
    - Model tracking (faster-whisper-large-v3)
    - Full-text search
    """
    __tablename__ = "transcriptions"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign key
    recording_id = Column(UUID(as_uuid=True), ForeignKey("recordings.id", ondelete="CASCADE"), nullable=False)

    # Transcription content
    full_text = Column(Text, nullable=False, default="")

    # Language
    language_code = Column(String(10), nullable=False, default="auto")  # 'fr-CA', 'en', 'auto'
    detected_language = Column(String(10), nullable=True)  # Actual detected language

    # Processing info
    model_used = Column(String(100), nullable=False, default="faster-whisper-large-v3")
    processing_time_seconds = Column(Float, nullable=True)
    word_count = Column(Integer, default=0)

    # Status
    status = Column(String(20), nullable=False, default=TranscriptionStatus.PENDING.value)
    error_message = Column(Text, nullable=True)

    # Timestamps
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Full-text search
    content_tsvector = Column(
        TSVECTOR,
        Computed("to_tsvector('english', coalesce(full_text, ''))", persisted=True)
    )

    # Relationships
    recording = relationship("Recording", back_populates="transcription")
    segments = relationship("TranscriptionSegment", back_populates="transcription", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('idx_transcriptions_recording_id', recording_id),
        Index('idx_transcriptions_status', status),
        Index('idx_transcriptions_content', content_tsvector, postgresql_using='gin'),
    )

    def __repr__(self):
        return f"<Transcription(id={self.id}, recording_id={self.recording_id})>"


class TranscriptionSegment(Base):
    """
    Transcription segment with timing information.

    Stores word-level timing for precise playback sync.
    """
    __tablename__ = "transcription_segments"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign key
    transcription_id = Column(UUID(as_uuid=True), ForeignKey("transcriptions.id", ondelete="CASCADE"), nullable=False)

    # Timing
    start_time = Column(Float, nullable=False)  # Seconds from recording start
    end_time = Column(Float, nullable=False)

    # Content
    text = Column(Text, nullable=False)
    confidence = Column(Float, nullable=True)  # 0.0 to 1.0
    speaker_id = Column(Integer, nullable=True)  # For future speaker diarization

    # Word-level data
    words = Column(JSONB, nullable=True)  # [{word: "hello", start: 0.5, end: 0.8, confidence: 0.95}, ...]

    # Bilingual/code-switching support
    language_detected = Column(String(10), nullable=True)  # 'fr', 'en', 'bilingual', or None
    language_confidence = Column(Float, nullable=True)  # 0.0 to 1.0
    is_code_switched = Column(Boolean, default=False)  # True if segment contains both languages

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    transcription = relationship("Transcription", back_populates="segments")

    # Indexes
    __table_args__ = (
        Index('idx_segments_transcription_id', transcription_id),
        Index('idx_segments_time_range', start_time, end_time),
    )

    def __repr__(self):
        text_preview = self.text[:30] if self.text else ""
        return f"<TranscriptionSegment(id={self.id}, text='{text_preview}...')>"
