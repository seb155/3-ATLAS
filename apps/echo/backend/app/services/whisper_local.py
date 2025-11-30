"""
Local Whisper transcription service using faster-whisper.

Provides GPU-accelerated speech-to-text with support for:
- French Canadian (fr-CA)
- English (en)
- Auto language detection
"""

import logging
from typing import Optional, Generator, List
from dataclasses import dataclass
from pathlib import Path
import os

from ..config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


@dataclass
class WordTiming:
    """Word-level timing information."""
    word: str
    start: float
    end: float
    probability: float


@dataclass
class TranscriptionSegment:
    """A segment of transcribed text with timing."""
    start: float
    end: float
    text: str
    words: List[WordTiming]
    avg_logprob: Optional[float] = None
    no_speech_prob: Optional[float] = None


@dataclass
class TranscriptionResult:
    """Complete transcription result."""
    text: str
    segments: List[TranscriptionSegment]
    language: str
    language_probability: float
    duration: float


class LocalWhisperService:
    """
    Local Whisper transcription service using faster-whisper.

    Features:
    - GPU acceleration (CUDA) with CPU fallback
    - French Canadian and English support
    - Auto language detection
    - Word-level timestamps
    - Voice Activity Detection (VAD)
    """

    def __init__(self):
        self.model = None
        self.model_size = settings.whisper_model
        self.device = settings.whisper_device
        self.compute_type = settings.whisper_compute_type
        self._is_loaded = False

    @property
    def is_available(self) -> bool:
        """Check if the service is available (model loaded)."""
        return self._is_loaded

    def load_model(self, force_reload: bool = False) -> bool:
        """
        Load the Whisper model.

        Args:
            force_reload: Force reload even if already loaded

        Returns:
            True if model loaded successfully
        """
        if self._is_loaded and not force_reload:
            return True

        try:
            from faster_whisper import WhisperModel

            logger.info(f"Loading Whisper model: {self.model_size} on {self.device}")

            # Check for CUDA availability
            if self.device == "cuda":
                try:
                    import torch
                    if not torch.cuda.is_available():
                        logger.warning("CUDA not available, falling back to CPU")
                        self.device = "cpu"
                        self.compute_type = "int8"
                except ImportError:
                    logger.warning("PyTorch not installed, falling back to CPU")
                    self.device = "cpu"
                    self.compute_type = "int8"

            # Model download directory
            model_dir = Path(settings.audio_storage_path) / "models"
            model_dir.mkdir(parents=True, exist_ok=True)

            self.model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type,
                download_root=str(model_dir),
            )

            self._is_loaded = True
            logger.info(f"Whisper model loaded successfully on {self.device}")
            return True

        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            self._is_loaded = False
            return False

    def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None,
        task: str = "transcribe",
    ) -> TranscriptionResult:
        """
        Transcribe an audio file.

        Args:
            audio_path: Path to the audio file
            language: Language code (None for auto-detect, 'fr' for French, 'en' for English)
            task: 'transcribe' or 'translate'

        Returns:
            TranscriptionResult with full text, segments, and metadata
        """
        if not self._is_loaded:
            if not self.load_model():
                raise RuntimeError("Failed to load Whisper model")

        # Validate file exists
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        logger.info(f"Transcribing: {audio_path} (language={language})")

        # Transcribe with faster-whisper
        segments, info = self.model.transcribe(
            audio_path,
            language=language,
            task=task,
            beam_size=5,
            vad_filter=True,
            vad_parameters=dict(
                min_silence_duration_ms=500,
                speech_pad_ms=400,
            ),
            word_timestamps=True,
        )

        # Collect results
        all_segments = []
        full_text_parts = []

        for segment in segments:
            words = []
            if segment.words:
                for w in segment.words:
                    words.append(WordTiming(
                        word=w.word,
                        start=w.start,
                        end=w.end,
                        probability=w.probability,
                    ))

            ts = TranscriptionSegment(
                start=segment.start,
                end=segment.end,
                text=segment.text.strip(),
                words=words,
                avg_logprob=segment.avg_logprob,
                no_speech_prob=segment.no_speech_prob,
            )
            all_segments.append(ts)
            full_text_parts.append(segment.text.strip())

        result = TranscriptionResult(
            text=" ".join(full_text_parts),
            segments=all_segments,
            language=info.language,
            language_probability=info.language_probability,
            duration=info.duration,
        )

        logger.info(
            f"Transcription complete: {len(all_segments)} segments, "
            f"language={info.language} ({info.language_probability:.2%})"
        )

        return result

    def transcribe_streaming(
        self,
        audio_path: str,
        language: Optional[str] = None,
    ) -> Generator[TranscriptionSegment, None, None]:
        """
        Transcribe an audio file with streaming results.

        Yields segments as they are processed.

        Args:
            audio_path: Path to the audio file
            language: Language code (None for auto-detect)

        Yields:
            TranscriptionSegment objects as they are processed
        """
        if not self._is_loaded:
            if not self.load_model():
                raise RuntimeError("Failed to load Whisper model")

        segments, _ = self.model.transcribe(
            audio_path,
            language=language,
            beam_size=5,
            vad_filter=True,
            word_timestamps=True,
        )

        for segment in segments:
            words = []
            if segment.words:
                for w in segment.words:
                    words.append(WordTiming(
                        word=w.word,
                        start=w.start,
                        end=w.end,
                        probability=w.probability,
                    ))

            yield TranscriptionSegment(
                start=segment.start,
                end=segment.end,
                text=segment.text.strip(),
                words=words,
            )

    def detect_language(self, audio_path: str) -> tuple[str, float]:
        """
        Detect the language of an audio file.

        Args:
            audio_path: Path to the audio file

        Returns:
            Tuple of (language_code, probability)
        """
        if not self._is_loaded:
            if not self.load_model():
                raise RuntimeError("Failed to load Whisper model")

        # Use a short segment for detection
        _, info = self.model.transcribe(
            audio_path,
            language=None,
            beam_size=1,
            vad_filter=True,
        )

        # Consume the generator (we just need the info)
        # The generator must be consumed for info to be populated

        return info.language, info.language_probability

    def unload_model(self):
        """Unload the model to free memory."""
        if self.model is not None:
            del self.model
            self.model = None
            self._is_loaded = False

            # Force garbage collection
            import gc
            gc.collect()

            # Clear CUDA cache if available
            try:
                import torch
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            except ImportError:
                pass

            logger.info("Whisper model unloaded")


# Singleton instance
_whisper_service: Optional[LocalWhisperService] = None


def get_whisper_service() -> LocalWhisperService:
    """Get the singleton Whisper service instance."""
    global _whisper_service
    if _whisper_service is None:
        _whisper_service = LocalWhisperService()
    return _whisper_service
