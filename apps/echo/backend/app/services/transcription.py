"""
Transcription service orchestrator.

Handles the transcription workflow:
1. Receives transcription requests
2. Routes to local GPU (faster-whisper)
3. Stores results in database
"""

import logging
from typing import Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session

from ..models.recording import Recording, RecordingStatus
from ..models.transcription import Transcription, TranscriptionSegment, TranscriptionStatus
from ..config import get_settings
from .whisper_local import get_whisper_service, TranscriptionResult

settings = get_settings()
logger = logging.getLogger(__name__)


class TranscriptionService:
    """
    Orchestrates transcription using local GPU.

    Features:
    - GPU transcription with faster-whisper
    - Language auto-detection (FR-CA / EN)
    - Database persistence
    - Status tracking
    """

    def __init__(self, db: Session):
        self.db = db
        self.whisper = get_whisper_service()

    async def transcribe_recording(
        self,
        recording_id: UUID,
        language: str = "auto",
    ) -> Transcription:
        """
        Transcribe a recording.

        Args:
            recording_id: ID of the recording to transcribe
            language: Language code ('auto', 'fr', 'en')

        Returns:
            Transcription object with results
        """
        # Get recording
        recording = self.db.query(Recording).filter(
            Recording.id == recording_id,
        ).first()

        if not recording:
            raise ValueError(f"Recording not found: {recording_id}")

        # Get or create transcription
        transcription = self.db.query(Transcription).filter(
            Transcription.recording_id == recording_id,
        ).first()

        if not transcription:
            transcription = Transcription(
                recording_id=recording_id,
                language_code=language,
            )
            self.db.add(transcription)
            self.db.commit()
            self.db.refresh(transcription)

        # Update status
        transcription.status = TranscriptionStatus.PROCESSING.value
        transcription.started_at = datetime.utcnow()
        recording.status = RecordingStatus.TRANSCRIBING.value
        self.db.commit()

        try:
            # Build audio path
            audio_path = f"{settings.audio_storage_path}/{recording.file_path}"

            # Determine language
            whisper_language = None if language == "auto" else language

            # Run transcription
            logger.info(f"Starting transcription for recording {recording_id}")
            start_time = datetime.utcnow()

            result = self.whisper.transcribe(
                audio_path=audio_path,
                language=whisper_language,
            )

            end_time = datetime.utcnow()
            processing_time = (end_time - start_time).total_seconds()

            # Store results
            transcription.full_text = result.text
            transcription.detected_language = result.language
            transcription.model_used = f"faster-whisper-{settings.whisper_model}"
            transcription.processing_time_seconds = processing_time
            transcription.word_count = len(result.text.split())
            transcription.status = TranscriptionStatus.COMPLETED.value
            transcription.completed_at = end_time

            # Store segments
            self._store_segments(transcription.id, result)

            # Update recording status
            recording.status = RecordingStatus.TRANSCRIBED.value

            self.db.commit()
            self.db.refresh(transcription)

            logger.info(
                f"Transcription complete for {recording_id}: "
                f"{transcription.word_count} words in {processing_time:.1f}s"
            )

            return transcription

        except Exception as e:
            logger.error(f"Transcription failed for {recording_id}: {e}")

            transcription.status = TranscriptionStatus.ERROR.value
            transcription.error_message = str(e)
            recording.status = RecordingStatus.ERROR.value

            self.db.commit()
            raise

    def _store_segments(
        self,
        transcription_id: UUID,
        result: TranscriptionResult,
    ):
        """Store transcription segments in database."""
        # Delete existing segments
        self.db.query(TranscriptionSegment).filter(
            TranscriptionSegment.transcription_id == transcription_id,
        ).delete()

        # Add new segments
        for segment in result.segments:
            # Convert words to JSON-serializable format
            words_data = None
            if segment.words:
                words_data = [
                    {
                        "word": w.word,
                        "start": w.start,
                        "end": w.end,
                        "confidence": w.probability,
                    }
                    for w in segment.words
                ]

            db_segment = TranscriptionSegment(
                transcription_id=transcription_id,
                start_time=segment.start,
                end_time=segment.end,
                text=segment.text,
                confidence=segment.avg_logprob,
                words=words_data,
            )
            self.db.add(db_segment)

    def get_transcription_status(
        self,
        transcription_id: UUID,
    ) -> dict:
        """Get transcription status."""
        transcription = self.db.query(Transcription).filter(
            Transcription.id == transcription_id,
        ).first()

        if not transcription:
            raise ValueError(f"Transcription not found: {transcription_id}")

        return {
            "id": transcription.id,
            "status": transcription.status,
            "error_message": transcription.error_message,
            "processing_time": transcription.processing_time_seconds,
        }


def get_transcription_service(db: Session) -> TranscriptionService:
    """Get a TranscriptionService instance."""
    return TranscriptionService(db)
