"""
Unified Transcription Service with Hardware Auto-Detection.

Automatically selects the best available hardware accelerator:
1. NPU (AMD Ryzen AI) - Highest priority, most efficient
2. GPU (CUDA/ROCm) - Fast but Radeon 890M not supported
3. CPU (faster-whisper) - Always available fallback

This service acts as a facade over the specific hardware implementations.
"""

import logging
from typing import Optional, List, Generator
from dataclasses import dataclass
from enum import Enum

from ..config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class TranscriptionDevice(Enum):
    """Available transcription hardware devices."""
    NPU = "npu"      # AMD Ryzen AI NPU (XDNA)
    GPU = "gpu"      # CUDA/ROCm GPU
    CPU = "cpu"      # CPU with faster-whisper
    AUTO = "auto"    # Auto-detect best available


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
    device: str  # Which device was used: 'npu', 'gpu', 'cpu'
    model: str   # Which model was used


class TranscriptionService:
    """
    Unified transcription service with automatic hardware detection.

    Priority order:
    1. NPU (AMD Ryzen AI) - Best for Ryzen AI 300 series
    2. GPU (CUDA) - For NVIDIA GPUs
    3. CPU - Always available fallback

    Note: AMD Radeon 890M (gfx1150) is NOT supported by ROCm,
    so GPU acceleration is skipped for this hardware.
    """

    def __init__(self, preferred_device: TranscriptionDevice = TranscriptionDevice.AUTO):
        self.preferred_device = preferred_device
        self._active_device: Optional[TranscriptionDevice] = None
        self._npu_service = None
        self._cpu_service = None
        self._is_initialized = False

    @property
    def active_device(self) -> Optional[TranscriptionDevice]:
        """Get the currently active transcription device."""
        return self._active_device

    @property
    def device_info(self) -> dict:
        """Get information about available devices."""
        return {
            "active": self._active_device.value if self._active_device else None,
            "npu_available": self._check_npu_available(),
            "gpu_available": self._check_gpu_available(),
            "cpu_available": True,  # Always available
            "preferred": self.preferred_device.value,
        }

    def _check_npu_available(self) -> bool:
        """Check if AMD NPU is available."""
        try:
            from .whisper_npu import NPUWhisperService
            return NPUWhisperService.is_npu_available()
        except ImportError:
            return False
        except Exception as e:
            logger.debug(f"NPU check failed: {e}")
            return False

    def _check_gpu_available(self) -> bool:
        """Check if CUDA GPU is available."""
        try:
            import torch
            if torch.cuda.is_available():
                # Check if it's an NVIDIA GPU (ROCm not supported for gfx1150)
                gpu_name = torch.cuda.get_device_name(0)
                if "NVIDIA" in gpu_name.upper():
                    return True
                else:
                    logger.info(f"GPU {gpu_name} detected but ROCm not fully supported")
                    return False
            return False
        except ImportError:
            return False
        except Exception:
            return False

    def initialize(self, force_device: Optional[TranscriptionDevice] = None) -> TranscriptionDevice:
        """
        Initialize the transcription service with the best available device.

        Args:
            force_device: Force a specific device (overrides auto-detection)

        Returns:
            The device that was initialized
        """
        device_to_use = force_device or self.preferred_device

        if device_to_use == TranscriptionDevice.AUTO:
            device_to_use = self._detect_best_device()

        logger.info(f"Initializing transcription service with device: {device_to_use.value}")

        if device_to_use == TranscriptionDevice.NPU:
            if self._initialize_npu():
                self._active_device = TranscriptionDevice.NPU
                self._is_initialized = True
                return self._active_device
            else:
                logger.warning("NPU initialization failed, falling back to CPU")
                device_to_use = TranscriptionDevice.CPU

        if device_to_use == TranscriptionDevice.GPU:
            # For now, skip GPU as Radeon 890M (gfx1150) is not supported
            logger.info("GPU transcription skipped (Radeon 890M gfx1150 not supported by ROCm)")
            device_to_use = TranscriptionDevice.CPU

        # CPU fallback
        if self._initialize_cpu():
            self._active_device = TranscriptionDevice.CPU
            self._is_initialized = True
            return self._active_device

        raise RuntimeError("Failed to initialize any transcription backend")

    def _detect_best_device(self) -> TranscriptionDevice:
        """Detect the best available transcription device."""
        # Priority 1: NPU (most efficient for Ryzen AI)
        if self._check_npu_available():
            logger.info("AMD Ryzen AI NPU detected - using NPU for transcription")
            return TranscriptionDevice.NPU

        # Priority 2: GPU (NVIDIA only - ROCm gfx1150 not supported)
        if self._check_gpu_available():
            logger.info("NVIDIA GPU detected - using GPU for transcription")
            return TranscriptionDevice.GPU

        # Priority 3: CPU (always available)
        logger.info("Using CPU for transcription (NPU/GPU not available)")
        return TranscriptionDevice.CPU

    def _initialize_npu(self) -> bool:
        """Initialize NPU transcription backend."""
        try:
            from .whisper_npu import get_npu_whisper_service
            self._npu_service = get_npu_whisper_service()
            return self._npu_service.load_model()
        except ImportError as e:
            logger.warning(f"NPU service not available: {e}")
            return False
        except Exception as e:
            logger.error(f"NPU initialization failed: {e}")
            return False

    def _initialize_cpu(self) -> bool:
        """Initialize CPU transcription backend."""
        try:
            from .whisper_local import get_whisper_service
            self._cpu_service = get_whisper_service()
            return self._cpu_service.load_model()
        except Exception as e:
            logger.error(f"CPU initialization failed: {e}")
            return False

    def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None,
    ) -> TranscriptionResult:
        """
        Transcribe an audio file using the best available device.

        Args:
            audio_path: Path to the audio file
            language: Language code (None for auto-detect, 'fr' for French, 'en' for English)

        Returns:
            TranscriptionResult with full text, segments, and metadata
        """
        if not self._is_initialized:
            self.initialize()

        if self._active_device == TranscriptionDevice.NPU:
            return self._transcribe_npu(audio_path, language)
        else:
            return self._transcribe_cpu(audio_path, language)

    def _transcribe_npu(self, audio_path: str, language: Optional[str]) -> TranscriptionResult:
        """Transcribe using NPU."""
        result = self._npu_service.transcribe(audio_path, language)

        # Convert NPU result to unified format
        segments = []
        for seg in result.segments:
            words = [WordTiming(
                word=w.word,
                start=w.start,
                end=w.end,
                probability=w.probability
            ) for w in seg.words]

            segments.append(TranscriptionSegment(
                start=seg.start,
                end=seg.end,
                text=seg.text,
                words=words
            ))

        return TranscriptionResult(
            text=result.text,
            segments=segments,
            language=result.language,
            language_probability=result.language_probability,
            duration=result.duration,
            device="npu",
            model=self._npu_service.model_name
        )

    def _transcribe_cpu(self, audio_path: str, language: Optional[str]) -> TranscriptionResult:
        """Transcribe using CPU (faster-whisper)."""
        result = self._cpu_service.transcribe(audio_path, language)

        # Convert CPU result to unified format
        segments = []
        for seg in result.segments:
            words = [WordTiming(
                word=w.word,
                start=w.start,
                end=w.end,
                probability=w.probability
            ) for w in seg.words]

            segments.append(TranscriptionSegment(
                start=seg.start,
                end=seg.end,
                text=seg.text,
                words=words,
                avg_logprob=seg.avg_logprob,
                no_speech_prob=seg.no_speech_prob
            ))

        return TranscriptionResult(
            text=result.text,
            segments=segments,
            language=result.language,
            language_probability=result.language_probability,
            duration=result.duration,
            device="cpu",
            model=self._cpu_service.model_size
        )

    def transcribe_streaming(
        self,
        audio_path: str,
        language: Optional[str] = None,
    ) -> Generator[TranscriptionSegment, None, None]:
        """
        Transcribe with streaming results (CPU only for now).

        Args:
            audio_path: Path to the audio file
            language: Language code

        Yields:
            TranscriptionSegment objects as processed
        """
        if not self._is_initialized:
            self.initialize()

        # NPU doesn't support streaming yet, use CPU
        if self._active_device != TranscriptionDevice.CPU:
            logger.info("Streaming transcription using CPU (NPU doesn't support streaming)")

        if self._cpu_service is None:
            self._initialize_cpu()

        for seg in self._cpu_service.transcribe_streaming(audio_path, language):
            words = [WordTiming(
                word=w.word,
                start=w.start,
                end=w.end,
                probability=w.probability
            ) for w in seg.words]

            yield TranscriptionSegment(
                start=seg.start,
                end=seg.end,
                text=seg.text,
                words=words
            )

    def detect_language(self, audio_path: str) -> tuple[str, float]:
        """
        Detect the language of an audio file.

        Returns:
            Tuple of (language_code, probability)
        """
        if not self._is_initialized:
            self.initialize()

        # Use CPU service for language detection (more reliable)
        if self._cpu_service is None:
            self._initialize_cpu()

        return self._cpu_service.detect_language(audio_path)

    def unload(self):
        """Unload all models to free memory."""
        if self._npu_service:
            self._npu_service.unload_model()
            self._npu_service = None

        if self._cpu_service:
            self._cpu_service.unload_model()
            self._cpu_service = None

        self._active_device = None
        self._is_initialized = False
        logger.info("Transcription service unloaded")


# Singleton instance
_transcription_service: Optional[TranscriptionService] = None


def get_transcription_service() -> TranscriptionService:
    """Get the singleton transcription service instance."""
    global _transcription_service
    if _transcription_service is None:
        _transcription_service = TranscriptionService()
    return _transcription_service
