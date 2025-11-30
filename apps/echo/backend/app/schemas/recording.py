"""
Pydantic schemas for recordings.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from enum import Enum


class RecordingStatusEnum(str, Enum):
    RECORDING = "recording"
    COMPLETED = "completed"
    TRANSCRIBING = "transcribing"
    TRANSCRIBED = "transcribed"
    ERROR = "error"


class AudioSourceTypeEnum(str, Enum):
    MICROPHONE = "microphone"
    SYSTEM = "system"
    BOTH = "both"


class FolderEnum(str, Enum):
    NOTES_PERSO = "notes-perso"
    MEETINGS = "meetings"


# =============================================================================
# REQUEST SCHEMAS
# =============================================================================

class RecordingCreate(BaseModel):
    """Schema for creating a new recording."""
    title: Optional[str] = None
    description: Optional[str] = None
    folder: FolderEnum = FolderEnum.NOTES_PERSO
    source_type: AudioSourceTypeEnum = AudioSourceTypeEnum.MICROPHONE


class RecordingUpdate(BaseModel):
    """Schema for updating a recording."""
    title: Optional[str] = None
    description: Optional[str] = None
    folder: Optional[FolderEnum] = None


class RecordingStart(BaseModel):
    """Schema for starting a recording."""
    title: Optional[str] = None
    folder: FolderEnum = FolderEnum.NOTES_PERSO
    source_type: AudioSourceTypeEnum = AudioSourceTypeEnum.MICROPHONE
    language: str = "auto"  # auto, fr, en


# =============================================================================
# RESPONSE SCHEMAS
# =============================================================================

class TagResponse(BaseModel):
    """Tag response schema."""
    id: UUID
    name: str
    color: str

    class Config:
        from_attributes = True


class RecordingResponse(BaseModel):
    """Recording response schema."""
    id: UUID
    user_id: UUID
    filename: str
    file_path: str
    folder: str
    file_size_bytes: int
    duration_seconds: float
    sample_rate: int
    channels: int
    format: str
    source_type: str
    title: Optional[str]
    description: Optional[str]
    status: str
    recorded_at: datetime
    created_at: datetime
    updated_at: datetime
    tags: List[TagResponse] = []

    class Config:
        from_attributes = True


class RecordingListResponse(BaseModel):
    """Paginated list of recordings."""
    items: List[RecordingResponse]
    total: int
    page: int
    page_size: int
    pages: int


class RecordingStatusResponse(BaseModel):
    """Recording status response."""
    id: UUID
    status: str
    duration_seconds: float
    is_transcribed: bool = False
