"""
Recording endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List
from uuid import UUID
from datetime import datetime
import os
import logging

from ...database import get_db, SessionLocal
from ...models.recording import Recording, RecordingStatus
from ...schemas.recording import (
    RecordingCreate,
    RecordingUpdate,
    RecordingResponse,
    RecordingListResponse,
    FolderEnum,
)
from ...config import get_settings
from ...services.transcription_service import TranscriptionService

router = APIRouter()
settings = get_settings()
logger = logging.getLogger(__name__)

# Placeholder user_id (will be replaced with auth)
DEMO_USER_ID = UUID("00000000-0000-0000-0000-000000000001")


def run_transcription_task(
    recording_id: UUID,
    transcription_id: UUID,
    audio_path: str,
    language: str,
):
    """
    Background task to run Whisper transcription.

    Uses a new DB session since this runs in a background thread.
    """
    db = SessionLocal()
    try:
        from ...models.transcription import Transcription, TranscriptionStatus

        transcription = db.query(Transcription).filter(
            Transcription.id == transcription_id
        ).first()

        if not transcription:
            logger.error(f"Transcription {transcription_id} not found")
            return

        recording = db.query(Recording).filter(
            Recording.id == recording_id
        ).first()

        if not recording:
            logger.error(f"Recording {recording_id} not found")
            return

        # Update status to processing
        transcription.status = TranscriptionStatus.PROCESSING.value
        transcription.started_at = datetime.utcnow()
        db.commit()

        logger.info(f"Starting transcription for {recording_id} with language={language}")

        # Run Whisper transcription
        service = TranscriptionService()
        whisper_lang = None if language in ("auto", "bilingual") else language
        result = service.transcribe(audio_path, language=whisper_lang)

        # Update transcription with result
        transcription.full_text = result.text
        transcription.detected_language = result.language
        transcription.model_used = result.model
        transcription.processing_time_seconds = result.duration
        transcription.word_count = len(result.text.split())
        transcription.status = TranscriptionStatus.COMPLETED.value
        transcription.completed_at = datetime.utcnow()

        # Update recording status
        recording.status = RecordingStatus.TRANSCRIBED.value

        db.commit()
        logger.info(f"Transcription completed for {recording_id}: {len(result.text)} chars")

    except Exception as e:
        logger.error(f"Transcription failed for {recording_id}: {e}")
        try:
            if transcription:
                transcription.status = TranscriptionStatus.FAILED.value
                transcription.error_message = str(e)
                db.commit()
        except Exception:
            pass
    finally:
        db.close()


# =============================================================================
# LIST & GET
# =============================================================================

@router.get("", response_model=RecordingListResponse)
async def list_recordings(
    folder: Optional[FolderEnum] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    List recordings with optional filters.

    - **folder**: Filter by folder (notes-perso, meetings)
    - **status**: Filter by status
    - **search**: Full-text search in title/description
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)
    """
    query = db.query(Recording).filter(
        Recording.user_id == DEMO_USER_ID,
        Recording.deleted_at.is_(None),
    )

    # Apply filters
    if folder:
        query = query.filter(Recording.folder == folder.value)
    if status:
        query = query.filter(Recording.status == status)
    if search:
        query = query.filter(
            Recording.search_vector.match(search)
        )

    # Count total
    total = query.count()

    # Paginate
    offset = (page - 1) * page_size
    items = query.order_by(desc(Recording.recorded_at)).offset(offset).limit(page_size).all()

    return RecordingListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.get("/{recording_id}", response_model=RecordingResponse)
async def get_recording(
    recording_id: UUID,
    db: Session = Depends(get_db),
):
    """Get a single recording by ID."""
    recording = db.query(Recording).filter(
        Recording.id == recording_id,
        Recording.user_id == DEMO_USER_ID,
        Recording.deleted_at.is_(None),
    ).first()

    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")

    return recording


@router.get("/{recording_id}/transcription")
async def get_recording_transcription(
    recording_id: UUID,
    db: Session = Depends(get_db),
):
    """Get the transcription for a recording."""
    from ...models.transcription import Transcription

    recording = db.query(Recording).filter(
        Recording.id == recording_id,
        Recording.user_id == DEMO_USER_ID,
        Recording.deleted_at.is_(None),
    ).first()

    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")

    transcription = db.query(Transcription).filter(
        Transcription.recording_id == recording_id
    ).first()

    if not transcription:
        raise HTTPException(status_code=404, detail="Transcription not found")

    return {
        "id": str(transcription.id),
        "recording_id": str(transcription.recording_id),
        "full_text": transcription.full_text,
        "language_code": transcription.language_code,
        "detected_language": transcription.detected_language,
        "model_used": transcription.model_used,
        "processing_time_seconds": transcription.processing_time_seconds,
        "word_count": transcription.word_count,
        "status": transcription.status,
        "error_message": transcription.error_message,
        "started_at": transcription.started_at.isoformat() if transcription.started_at else None,
        "completed_at": transcription.completed_at.isoformat() if transcription.completed_at else None,
        "created_at": transcription.created_at.isoformat() if transcription.created_at else None,
        "updated_at": transcription.updated_at.isoformat() if transcription.updated_at else None,
    }


# =============================================================================
# CREATE & UPDATE
# =============================================================================

@router.post("", response_model=RecordingResponse)
async def create_recording(
    data: RecordingCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new recording metadata entry.

    Audio data will be uploaded separately via the audio endpoint.
    """
    # Generate filename
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    title_slug = data.title.replace(" ", "-")[:30] if data.title else "recording"
    filename = f"{timestamp}_{title_slug}.wav"

    # Create file path
    file_path = f"{data.folder.value}/{filename}"

    recording = Recording(
        user_id=DEMO_USER_ID,
        filename=filename,
        file_path=file_path,
        folder=data.folder.value,
        source_type=data.source_type.value,
        title=data.title,
        description=data.description,
        status=RecordingStatus.RECORDING.value,
    )

    db.add(recording)
    db.commit()
    db.refresh(recording)

    return recording


@router.patch("/{recording_id}", response_model=RecordingResponse)
async def update_recording(
    recording_id: UUID,
    data: RecordingUpdate,
    db: Session = Depends(get_db),
):
    """Update recording metadata."""
    recording = db.query(Recording).filter(
        Recording.id == recording_id,
        Recording.user_id == DEMO_USER_ID,
        Recording.deleted_at.is_(None),
    ).first()

    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")

    # Update fields
    if data.title is not None:
        recording.title = data.title
    if data.description is not None:
        recording.description = data.description
    if data.folder is not None:
        recording.folder = data.folder.value

    db.commit()
    db.refresh(recording)

    return recording


# =============================================================================
# DELETE
# =============================================================================

@router.delete("/{recording_id}")
async def delete_recording(
    recording_id: UUID,
    permanent: bool = False,
    db: Session = Depends(get_db),
):
    """
    Delete a recording.

    - **permanent**: If true, permanently delete. Otherwise, soft delete.
    """
    recording = db.query(Recording).filter(
        Recording.id == recording_id,
        Recording.user_id == DEMO_USER_ID,
    ).first()

    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")

    if permanent:
        # Delete file from disk
        full_path = os.path.join(settings.audio_storage_path, recording.file_path)
        if os.path.exists(full_path):
            os.remove(full_path)

        db.delete(recording)
    else:
        # Soft delete
        recording.deleted_at = datetime.utcnow()

    db.commit()

    return {"message": "Recording deleted", "permanent": permanent}


# =============================================================================
# DOWNLOAD
# =============================================================================

@router.get("/{recording_id}/download")
async def download_recording(
    recording_id: UUID,
    db: Session = Depends(get_db),
):
    """Download the audio file for a recording."""
    recording = db.query(Recording).filter(
        Recording.id == recording_id,
        Recording.user_id == DEMO_USER_ID,
        Recording.deleted_at.is_(None),
    ).first()

    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")

    full_path = os.path.join(settings.audio_storage_path, recording.file_path)

    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="Audio file not found")

    return FileResponse(
        full_path,
        media_type="audio/wav",
        filename=recording.filename,
    )


# =============================================================================
# TRANSCRIBE
# =============================================================================

@router.post("/{recording_id}/transcribe")
async def transcribe_recording(
    recording_id: UUID,
    language: str = "auto",
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
):
    """
    Start transcription for a recording.

    - **language**: Language code (auto, fr, en)

    Returns the created transcription with status "pending".
    """
    recording = db.query(Recording).filter(
        Recording.id == recording_id,
        Recording.user_id == DEMO_USER_ID,
        Recording.deleted_at.is_(None),
    ).first()

    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")

    if recording.status not in [RecordingStatus.COMPLETED.value, RecordingStatus.TRANSCRIBED.value]:
        raise HTTPException(
            status_code=400,
            detail=f"Recording must be completed before transcription. Current status: {recording.status}"
        )

    # Import here to avoid circular imports
    from ...models.transcription import Transcription, TranscriptionStatus

    # Check if transcription already exists
    existing = db.query(Transcription).filter(
        Transcription.recording_id == recording_id
    ).first()

    if existing:
        if existing.status == TranscriptionStatus.COMPLETED.value:
            raise HTTPException(status_code=400, detail="Recording already transcribed")
        # Reset if failed/pending
        existing.status = TranscriptionStatus.PENDING.value
        existing.error_message = None
        db.commit()
        return {"message": "Transcription restarted", "transcription_id": existing.id}

    # Create new transcription
    transcription = Transcription(
        recording_id=recording_id,
        language_code=language,
        status=TranscriptionStatus.PENDING.value,
    )

    db.add(transcription)

    # Update recording status
    recording.status = RecordingStatus.TRANSCRIBING.value

    db.commit()
    db.refresh(transcription)

    # Build audio file path
    audio_path = os.path.join(settings.audio_storage_path, recording.file_path)

    # Trigger async transcription job
    if background_tasks:
        background_tasks.add_task(
            run_transcription_task,
            recording_id=recording.id,
            transcription_id=transcription.id,
            audio_path=audio_path,
            language=language,
        )
        logger.info(f"Queued transcription task for recording {recording_id}")
    else:
        # Fallback: run synchronously if no background_tasks
        logger.warning(f"Running transcription synchronously for {recording_id}")
        run_transcription_task(
            recording_id=recording.id,
            transcription_id=transcription.id,
            audio_path=audio_path,
            language=language,
        )

    return {
        "message": "Transcription started",
        "transcription_id": transcription.id,
        "status": transcription.status,
    }
