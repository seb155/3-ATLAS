"""
Audio capture endpoints.

These endpoints interface with the Tauri desktop app for
audio recording control.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID
from datetime import datetime
import os
import wave
import struct

from ...database import get_db
from ...models.recording import Recording, RecordingStatus
from ...schemas.recording import RecordingStart, AudioSourceTypeEnum
from ...config import get_settings

router = APIRouter()
settings = get_settings()

# Placeholder user_id
DEMO_USER_ID = UUID("00000000-0000-0000-0000-000000000001")


# =============================================================================
# DEVICE LISTING
# =============================================================================

@router.get("/devices")
async def list_audio_devices():
    """
    List available audio devices.

    This is a placeholder - actual device enumeration happens in Tauri.
    The frontend will call this to get device info from the Tauri backend.
    """
    return {
        "input_devices": [
            {"id": "default", "name": "Default Microphone", "is_default": True},
        ],
        "output_devices": [
            {"id": "default", "name": "Default Speaker (Loopback)", "is_default": True},
        ],
        "note": "Device enumeration handled by Tauri desktop app"
    }


# =============================================================================
# RECORDING CONTROL
# =============================================================================

@router.post("/start")
async def start_recording(
    data: RecordingStart,
    db: Session = Depends(get_db),
):
    """
    Start a new recording.

    Creates the recording metadata and returns the recording ID.
    The Tauri app will use this ID to associate the audio file.
    """
    # Generate filename
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    title_slug = data.title.replace(" ", "-")[:30] if data.title else "recording"
    filename = f"{timestamp}_{title_slug}.wav"

    # Create file path
    file_path = f"{data.folder.value}/{filename}"

    # Create recording entry
    recording = Recording(
        user_id=DEMO_USER_ID,
        filename=filename,
        file_path=file_path,
        folder=data.folder.value,
        source_type=data.source_type.value,
        title=data.title,
        status=RecordingStatus.RECORDING.value,
    )

    db.add(recording)
    db.commit()
    db.refresh(recording)

    # Ensure directory exists
    full_dir = os.path.join(settings.audio_storage_path, data.folder.value)
    os.makedirs(full_dir, exist_ok=True)

    return {
        "recording_id": recording.id,
        "filename": filename,
        "file_path": file_path,
        "full_path": os.path.join(settings.audio_storage_path, file_path),
        "source_type": data.source_type.value,
        "language": data.language,
    }


@router.post("/stop/{recording_id}")
async def stop_recording(
    recording_id: UUID,
    duration_seconds: float = 0,
    file_size_bytes: int = 0,
    db: Session = Depends(get_db),
):
    """
    Stop an active recording.

    Updates the recording status and metadata.
    Called by Tauri after audio capture is complete.
    """
    recording = db.query(Recording).filter(
        Recording.id == recording_id,
        Recording.user_id == DEMO_USER_ID,
    ).first()

    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")

    if recording.status != RecordingStatus.RECORDING.value:
        raise HTTPException(
            status_code=400,
            detail=f"Recording is not active. Status: {recording.status}"
        )

    # Update recording
    recording.status = RecordingStatus.COMPLETED.value
    recording.duration_seconds = duration_seconds
    recording.file_size_bytes = file_size_bytes

    # Try to get actual file info
    full_path = os.path.join(settings.audio_storage_path, recording.file_path)
    if os.path.exists(full_path):
        recording.file_size_bytes = os.path.getsize(full_path)

        # Try to read WAV duration
        try:
            with wave.open(full_path, 'rb') as wav:
                frames = wav.getnframes()
                rate = wav.getframerate()
                recording.duration_seconds = frames / float(rate)
                recording.sample_rate = rate
                recording.channels = wav.getnchannels()
        except Exception:
            pass

    db.commit()
    db.refresh(recording)

    return {
        "recording_id": recording.id,
        "status": recording.status,
        "duration_seconds": recording.duration_seconds,
        "file_size_bytes": recording.file_size_bytes,
    }


@router.get("/status/{recording_id}")
async def get_recording_status(
    recording_id: UUID,
    db: Session = Depends(get_db),
):
    """Get the status of an active recording."""
    recording = db.query(Recording).filter(
        Recording.id == recording_id,
        Recording.user_id == DEMO_USER_ID,
    ).first()

    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")

    return {
        "recording_id": recording.id,
        "status": recording.status,
        "duration_seconds": recording.duration_seconds,
        "source_type": recording.source_type,
    }


# =============================================================================
# FILE UPLOAD
# =============================================================================

@router.post("/upload/{recording_id}")
async def upload_audio(
    recording_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload audio file for a recording.

    Alternative to Tauri direct file writing.
    Useful for web-based recording or testing.
    """
    recording = db.query(Recording).filter(
        Recording.id == recording_id,
        Recording.user_id == DEMO_USER_ID,
    ).first()

    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")

    # Ensure directory exists
    full_dir = os.path.join(settings.audio_storage_path, recording.folder)
    os.makedirs(full_dir, exist_ok=True)

    # Save file
    full_path = os.path.join(settings.audio_storage_path, recording.file_path)

    with open(full_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Update recording
    recording.file_size_bytes = os.path.getsize(full_path)
    recording.status = RecordingStatus.COMPLETED.value

    # Try to read WAV info
    try:
        with wave.open(full_path, 'rb') as wav:
            frames = wav.getnframes()
            rate = wav.getframerate()
            recording.duration_seconds = frames / float(rate)
            recording.sample_rate = rate
            recording.channels = wav.getnchannels()
    except Exception:
        pass

    db.commit()
    db.refresh(recording)

    return {
        "recording_id": recording.id,
        "status": recording.status,
        "file_size_bytes": recording.file_size_bytes,
        "duration_seconds": recording.duration_seconds,
    }
