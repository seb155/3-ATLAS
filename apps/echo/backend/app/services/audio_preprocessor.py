"""
Audio preprocessing utilities for transcription quality.

Handles:
- Pre-padding to prevent word cutoff at the beginning
- Post-padding for clean segment endings
- Sample rate normalization to 16kHz (Whisper requirement)
"""

import logging
import tempfile
import os
from pathlib import Path
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

# Whisper requires 16kHz audio
TARGET_SAMPLE_RATE = 16000

# Padding durations (milliseconds)
PRE_PADDING_MS = 500   # Silence before audio to prevent word cutoff
POST_PADDING_MS = 300  # Silence after audio for clean endings


def preprocess_audio_for_transcription(
    audio_path: str,
    pre_pad_ms: int = PRE_PADDING_MS,
    post_pad_ms: int = POST_PADDING_MS,
    target_sr: int = TARGET_SAMPLE_RATE,
) -> Tuple[str, bool]:
    """
    Preprocess audio file for optimal transcription.

    Adds silence padding at the beginning and end of the audio to prevent
    word cutoff issues that can occur with VAD (Voice Activity Detection).

    Args:
        audio_path: Path to the input audio file
        pre_pad_ms: Milliseconds of silence to add before audio (default: 500ms)
        post_pad_ms: Milliseconds of silence to add after audio (default: 300ms)
        target_sr: Target sample rate (default: 16000 for Whisper)

    Returns:
        Tuple of (preprocessed_audio_path, is_temporary)
        - preprocessed_audio_path: Path to the processed audio file
        - is_temporary: True if the file should be deleted after use
    """
    try:
        import librosa
        import soundfile as sf
        import numpy as np
    except ImportError as e:
        logger.warning(f"Audio preprocessing dependencies not available: {e}")
        logger.info("Falling back to original audio without preprocessing")
        return audio_path, False

    try:
        # Load audio with target sample rate
        logger.debug(f"Loading audio: {audio_path}")
        audio, sr = librosa.load(audio_path, sr=target_sr, mono=True)

        original_duration = len(audio) / sr
        logger.debug(f"Original audio: {original_duration:.2f}s, {len(audio)} samples @ {sr}Hz")

        # Calculate padding samples
        pre_pad_samples = int(target_sr * pre_pad_ms / 1000)
        post_pad_samples = int(target_sr * post_pad_ms / 1000)

        # Create low-noise silence (not completely silent to avoid artifacts)
        # Using very low amplitude noise instead of zeros
        pre_silence = np.random.normal(0, 0.0001, pre_pad_samples).astype(np.float32)
        post_silence = np.random.normal(0, 0.0001, post_pad_samples).astype(np.float32)

        # Normalize audio to prevent clipping
        max_val = np.abs(audio).max()
        if max_val > 0:
            audio = audio / max_val * 0.95

        # Concatenate: silence + audio + silence
        padded_audio = np.concatenate([pre_silence, audio, post_silence])

        # Create temporary file for preprocessed audio
        temp_dir = Path(tempfile.gettempdir()) / "echo_preprocessed"
        temp_dir.mkdir(exist_ok=True)

        # Use original filename with prefix
        original_name = Path(audio_path).stem
        temp_path = temp_dir / f"preprocessed_{original_name}.wav"

        # Write preprocessed audio
        sf.write(str(temp_path), padded_audio, target_sr)

        new_duration = len(padded_audio) / sr
        logger.info(
            f"Audio preprocessed: {original_duration:.2f}s -> {new_duration:.2f}s "
            f"(+{pre_pad_ms}ms pre, +{post_pad_ms}ms post)"
        )

        return str(temp_path), True

    except Exception as e:
        logger.error(f"Audio preprocessing failed: {e}")
        logger.info("Falling back to original audio")
        return audio_path, False


def cleanup_preprocessed_file(file_path: str) -> None:
    """
    Remove a temporary preprocessed audio file.

    Args:
        file_path: Path to the file to remove
    """
    try:
        if os.path.exists(file_path) and "preprocessed_" in os.path.basename(file_path):
            os.remove(file_path)
            logger.debug(f"Cleaned up preprocessed file: {file_path}")
    except Exception as e:
        logger.warning(f"Failed to cleanup preprocessed file: {e}")


def cleanup_old_preprocessed_files(max_age_hours: int = 24) -> int:
    """
    Clean up old preprocessed files from the temp directory.

    Args:
        max_age_hours: Remove files older than this many hours

    Returns:
        Number of files removed
    """
    import time

    temp_dir = Path(tempfile.gettempdir()) / "echo_preprocessed"
    if not temp_dir.exists():
        return 0

    removed = 0
    max_age_seconds = max_age_hours * 3600
    current_time = time.time()

    try:
        for file_path in temp_dir.glob("preprocessed_*.wav"):
            try:
                file_age = current_time - file_path.stat().st_mtime
                if file_age > max_age_seconds:
                    file_path.unlink()
                    removed += 1
            except Exception as e:
                logger.debug(f"Could not remove old file {file_path}: {e}")

        if removed > 0:
            logger.info(f"Cleaned up {removed} old preprocessed files")

    except Exception as e:
        logger.warning(f"Cleanup of old preprocessed files failed: {e}")

    return removed


class AudioPreprocessor:
    """
    Audio preprocessor with context manager support for automatic cleanup.

    Usage:
        with AudioPreprocessor(audio_path) as processed_path:
            # Use processed_path for transcription
            result = transcribe(processed_path)
        # Temporary file is automatically cleaned up
    """

    def __init__(
        self,
        audio_path: str,
        pre_pad_ms: int = PRE_PADDING_MS,
        post_pad_ms: int = POST_PADDING_MS,
    ):
        self.original_path = audio_path
        self.pre_pad_ms = pre_pad_ms
        self.post_pad_ms = post_pad_ms
        self.processed_path: Optional[str] = None
        self.is_temporary: bool = False

    def __enter__(self) -> str:
        """Preprocess audio and return path to processed file."""
        self.processed_path, self.is_temporary = preprocess_audio_for_transcription(
            self.original_path,
            self.pre_pad_ms,
            self.post_pad_ms,
        )
        return self.processed_path

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up temporary file if created."""
        if self.is_temporary and self.processed_path:
            cleanup_preprocessed_file(self.processed_path)
        return False  # Don't suppress exceptions
