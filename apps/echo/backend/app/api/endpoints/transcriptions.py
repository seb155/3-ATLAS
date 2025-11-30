"""
Transcription endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from ...database import get_db
from ...models.transcription import Transcription, TranscriptionSegment, TranscriptionStatus
from ...models.recording import Recording, RecordingStatus
from ...schemas.transcription import (
    TranscriptionResponse,
    TranscriptionUpdate,
    TranscriptionStatusResponse,
    TranscriptionExport,
    SegmentResponse,
)
from ...config import get_settings

router = APIRouter()
settings = get_settings()

# Placeholder user_id
DEMO_USER_ID = UUID("00000000-0000-0000-0000-000000000001")


# =============================================================================
# GET
# =============================================================================

@router.get("/{transcription_id}", response_model=TranscriptionResponse)
async def get_transcription(
    transcription_id: UUID,
    db: Session = Depends(get_db),
):
    """Get a transcription by ID."""
    transcription = db.query(Transcription).filter(
        Transcription.id == transcription_id,
    ).first()

    if not transcription:
        raise HTTPException(status_code=404, detail="Transcription not found")

    # Verify ownership via recording
    recording = db.query(Recording).filter(
        Recording.id == transcription.recording_id,
        Recording.user_id == DEMO_USER_ID,
    ).first()

    if not recording:
        raise HTTPException(status_code=404, detail="Transcription not found")

    return transcription


@router.get("/{transcription_id}/status", response_model=TranscriptionStatusResponse)
async def get_transcription_status(
    transcription_id: UUID,
    db: Session = Depends(get_db),
):
    """Get transcription status for polling."""
    transcription = db.query(Transcription).filter(
        Transcription.id == transcription_id,
    ).first()

    if not transcription:
        raise HTTPException(status_code=404, detail="Transcription not found")

    # Calculate progress (placeholder)
    progress = 0.0
    if transcription.status == TranscriptionStatus.PROCESSING.value:
        progress = 0.5  # Will be updated with actual progress
    elif transcription.status == TranscriptionStatus.COMPLETED.value:
        progress = 1.0

    return TranscriptionStatusResponse(
        id=transcription.id,
        status=transcription.status,
        progress=progress,
        error_message=transcription.error_message,
    )


@router.get("/{transcription_id}/segments")
async def get_transcription_segments(
    transcription_id: UUID,
    db: Session = Depends(get_db),
):
    """Get all segments for a transcription."""
    transcription = db.query(Transcription).filter(
        Transcription.id == transcription_id,
    ).first()

    if not transcription:
        raise HTTPException(status_code=404, detail="Transcription not found")

    segments = db.query(TranscriptionSegment).filter(
        TranscriptionSegment.transcription_id == transcription_id,
    ).order_by(TranscriptionSegment.start_time).all()

    return {"segments": segments}


# =============================================================================
# UPDATE
# =============================================================================

@router.patch("/{transcription_id}", response_model=TranscriptionResponse)
async def update_transcription(
    transcription_id: UUID,
    data: TranscriptionUpdate,
    db: Session = Depends(get_db),
):
    """Update transcription text (manual editing)."""
    transcription = db.query(Transcription).filter(
        Transcription.id == transcription_id,
    ).first()

    if not transcription:
        raise HTTPException(status_code=404, detail="Transcription not found")

    # Verify ownership
    recording = db.query(Recording).filter(
        Recording.id == transcription.recording_id,
        Recording.user_id == DEMO_USER_ID,
    ).first()

    if not recording:
        raise HTTPException(status_code=404, detail="Transcription not found")

    transcription.full_text = data.full_text
    transcription.word_count = len(data.full_text.split())

    db.commit()
    db.refresh(transcription)

    return transcription


# =============================================================================
# EXPORT
# =============================================================================

@router.post("/{transcription_id}/export")
async def export_transcription(
    transcription_id: UUID,
    export: TranscriptionExport,
    db: Session = Depends(get_db),
):
    """
    Export transcription in various formats.

    Supported formats:
    - txt: Plain text
    - srt: SubRip subtitle format
    - vtt: WebVTT subtitle format
    - json: JSON with segments
    """
    transcription = db.query(Transcription).filter(
        Transcription.id == transcription_id,
    ).first()

    if not transcription:
        raise HTTPException(status_code=404, detail="Transcription not found")

    if transcription.status != TranscriptionStatus.COMPLETED.value:
        raise HTTPException(status_code=400, detail="Transcription not completed")

    segments = db.query(TranscriptionSegment).filter(
        TranscriptionSegment.transcription_id == transcription_id,
    ).order_by(TranscriptionSegment.start_time).all()

    if export.format == "txt":
        return PlainTextResponse(
            content=transcription.full_text,
            media_type="text/plain",
        )

    elif export.format == "srt":
        srt_content = _generate_srt(segments)
        return PlainTextResponse(
            content=srt_content,
            media_type="text/plain",
            headers={"Content-Disposition": f"attachment; filename=transcription_{transcription_id}.srt"}
        )

    elif export.format == "vtt":
        vtt_content = _generate_vtt(segments)
        return PlainTextResponse(
            content=vtt_content,
            media_type="text/vtt",
            headers={"Content-Disposition": f"attachment; filename=transcription_{transcription_id}.vtt"}
        )

    elif export.format == "json":
        return {
            "transcription_id": transcription.id,
            "full_text": transcription.full_text,
            "language": transcription.detected_language or transcription.language_code,
            "segments": [
                {
                    "start": s.start_time,
                    "end": s.end_time,
                    "text": s.text,
                    "confidence": s.confidence,
                }
                for s in segments
            ]
        }

    else:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {export.format}")


def _format_srt_time(seconds: float) -> str:
    """Format seconds to SRT timestamp (HH:MM:SS,mmm)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def _format_vtt_time(seconds: float) -> str:
    """Format seconds to VTT timestamp (HH:MM:SS.mmm)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


def _generate_srt(segments) -> str:
    """Generate SRT subtitle content."""
    lines = []
    for i, segment in enumerate(segments, 1):
        lines.append(str(i))
        lines.append(f"{_format_srt_time(segment.start_time)} --> {_format_srt_time(segment.end_time)}")
        lines.append(segment.text)
        lines.append("")
    return "\n".join(lines)


def _generate_vtt(segments) -> str:
    """Generate WebVTT subtitle content."""
    lines = ["WEBVTT", ""]
    for segment in segments:
        lines.append(f"{_format_vtt_time(segment.start_time)} --> {_format_vtt_time(segment.end_time)}")
        lines.append(segment.text)
        lines.append("")
    return "\n".join(lines)


# =============================================================================
# WEBSOCKET (Real-time transcription)
# =============================================================================

@router.websocket("/live/{recording_id}")
async def live_transcription(
    websocket: WebSocket,
    recording_id: UUID,
    db: Session = Depends(get_db),
):
    """
    WebSocket endpoint for real-time transcription.

    The client can send audio chunks and receive transcription segments.
    """
    await websocket.accept()

    try:
        # Verify recording exists
        recording = db.query(Recording).filter(
            Recording.id == recording_id,
        ).first()

        if not recording:
            await websocket.send_json({"type": "error", "message": "Recording not found"})
            await websocket.close()
            return

        await websocket.send_json({
            "type": "status",
            "status": "connected",
            "message": "Ready for real-time transcription"
        })

        # Main WebSocket loop
        while True:
            data = await websocket.receive_json()

            if data.get("type") == "audio_chunk":
                # TODO: Process audio chunk with Whisper
                # For now, send a placeholder response
                await websocket.send_json({
                    "type": "segment",
                    "text": "[Processing audio...]",
                    "start_time": 0,
                    "end_time": 0,
                    "is_final": False,
                })

            elif data.get("type") == "stop":
                await websocket.send_json({
                    "type": "status",
                    "status": "stopped",
                    "message": "Transcription stopped"
                })
                break

    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({"type": "error", "message": str(e)})
    finally:
        await websocket.close()
