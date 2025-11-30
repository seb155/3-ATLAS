"""
Pydantic schemas for transcriptions.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum


class TranscriptionStatusEnum(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


class LanguageEnum(str, Enum):
    AUTO = "auto"
    FRENCH = "fr"
    ENGLISH = "en"
    BILINGUAL = "bilingual"  # French + English code-switching


# =============================================================================
# REQUEST SCHEMAS
# =============================================================================

class TranscriptionRequest(BaseModel):
    """Schema for starting a transcription."""
    language: LanguageEnum = LanguageEnum.AUTO
    real_time: bool = False  # Enable real-time transcription via WebSocket


class TranscriptionUpdate(BaseModel):
    """Schema for updating transcription text."""
    full_text: str


# =============================================================================
# RESPONSE SCHEMAS
# =============================================================================

class WordTiming(BaseModel):
    """Word-level timing information."""
    word: str
    start: float
    end: float
    confidence: Optional[float] = None


class SegmentResponse(BaseModel):
    """Transcription segment response."""
    id: UUID
    start_time: float
    end_time: float
    text: str
    confidence: Optional[float]
    speaker_id: Optional[int]
    words: Optional[List[WordTiming]] = None
    # Bilingual/code-switching fields
    language_detected: Optional[str] = None  # 'fr', 'en', 'bilingual'
    language_confidence: Optional[float] = None  # 0.0 to 1.0
    is_code_switched: bool = False  # True if segment contains both FR and EN

    class Config:
        from_attributes = True


class TranscriptionResponse(BaseModel):
    """Full transcription response."""
    id: UUID
    recording_id: UUID
    full_text: str
    language_code: str
    detected_language: Optional[str]
    model_used: str
    processing_time_seconds: Optional[float]
    word_count: int
    status: str
    error_message: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    segments: List[SegmentResponse] = []

    class Config:
        from_attributes = True


class TranscriptionStatusResponse(BaseModel):
    """Transcription status for polling."""
    id: UUID
    status: str
    progress: float = 0.0  # 0.0 to 1.0
    error_message: Optional[str] = None


class TranscriptionExport(BaseModel):
    """Schema for export request."""
    format: str = "txt"  # txt, srt, json, vtt


# =============================================================================
# WEBSOCKET SCHEMAS
# =============================================================================

class RealTimeSegment(BaseModel):
    """Real-time transcription segment sent via WebSocket."""
    type: str = "segment"
    text: str
    start_time: float
    end_time: float
    is_final: bool = False
    language: Optional[str] = None


class RealTimeStatus(BaseModel):
    """Real-time status update."""
    type: str = "status"
    status: str
    message: Optional[str] = None
