"""
AMD Ryzen AI NPU Whisper transcription service.

Provides NPU-accelerated speech-to-text using AMD Ryzen AI SDK.
Optimized for AMD Ryzen AI 300 series processors with XDNA NPU.

Requirements:
- AMD Ryzen AI SDK 1.6.1+
- NPU Driver MCDM v32.0.203.280+
- Windows 11

Supported models (from HuggingFace):
- amd/NPU-Whisper-Base-Small
- magicunicorn/whisper-medium-amd-npu-int8
- magicunicorn/whisper-large-v3-amd-npu-int8
"""

import logging
from typing import Optional, List
from dataclasses import dataclass
from pathlib import Path
import os

from ..config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


@dataclass
class NPUWordTiming:
    """Word-level timing information."""
    word: str
    start: float
    end: float
    probability: float = 1.0


@dataclass
class NPUTranscriptionSegment:
    """A segment of transcribed text with timing."""
    start: float
    end: float
    text: str
    words: List[NPUWordTiming]
    language_detected: Optional[str] = None  # 'fr', 'en', 'bilingual', or None
    language_confidence: float = 0.0
    is_code_switched: bool = False


@dataclass
class NPUTranscriptionResult:
    """Complete transcription result from NPU."""
    text: str
    segments: List[NPUTranscriptionSegment]
    language: str
    language_probability: float
    duration: float
    device: str = "npu"


class NPUWhisperService:
    """
    AMD Ryzen AI NPU Whisper transcription service.

    Uses the Ryzen AI SDK for NPU-accelerated inference.
    Supports BFP16 precision which provides better accuracy than INT8
    while maintaining high performance on the XDNA NPU.

    Features:
    - NPU acceleration (50 TOPS on Ryzen AI 9 HX 370)
    - French Canadian and English support
    - Auto language detection
    - Word-level timestamps (when supported)
    - Energy-efficient processing
    """

    def __init__(self):
        self.model = None
        self.processor = None
        self.model_name = settings.whisper_model_npu if hasattr(settings, 'whisper_model_npu') else "medium"
        self._is_loaded = False
        self._npu_available = None

    @staticmethod
    def is_npu_available() -> bool:
        """
        Check if AMD Ryzen AI NPU is available.

        Returns:
            True if NPU is available and SDK is installed
        """
        try:
            # Try to import Ryzen AI SDK
            # Note: The actual import may vary based on SDK version
            # This is a placeholder - adjust based on actual SDK API
            import onnxruntime as ort

            # Check for AMD EP (Execution Provider)
            providers = ort.get_available_providers()
            if 'VitisAIExecutionProvider' in providers or 'AMDNPUExecutionProvider' in providers:
                logger.info("AMD NPU Execution Provider detected")
                return True

            # Alternative: Check for Windows ML NPU support
            # This requires Windows 11 with NPU drivers
            if 'DmlExecutionProvider' in providers:
                # DirectML can use NPU on supported hardware
                logger.info("DirectML Execution Provider detected (may use NPU)")
                return True

            logger.debug(f"Available ONNX providers: {providers}")
            return False

        except ImportError as e:
            logger.debug(f"ONNX Runtime not available: {e}")
            return False
        except Exception as e:
            logger.debug(f"NPU availability check failed: {e}")
            return False

    @property
    def is_available(self) -> bool:
        """Check if the service is available (model loaded)."""
        return self._is_loaded

    def load_model(self, force_reload: bool = False) -> bool:
        """
        Load the Whisper model for NPU inference.

        Args:
            force_reload: Force reload even if already loaded

        Returns:
            True if model loaded successfully
        """
        if self._is_loaded and not force_reload:
            return True

        try:
            import onnxruntime as ort
            from transformers import WhisperProcessor

            logger.info(f"Loading Whisper model for NPU: {self.model_name}")

            # Model download directory
            model_dir = Path(settings.audio_storage_path) / "models" / "npu"
            model_dir.mkdir(parents=True, exist_ok=True)

            # Load processor for tokenization
            model_id = self._get_huggingface_model_id()
            self.processor = WhisperProcessor.from_pretrained(
                model_id,
                cache_dir=str(model_dir)
            )

            # Configure ONNX Runtime session for NPU
            providers = ort.get_available_providers()

            # Prefer AMD NPU providers
            if 'VitisAIExecutionProvider' in providers:
                ep_list = ['VitisAIExecutionProvider', 'CPUExecutionProvider']
            elif 'AMDNPUExecutionProvider' in providers:
                ep_list = ['AMDNPUExecutionProvider', 'CPUExecutionProvider']
            elif 'DmlExecutionProvider' in providers:
                # DirectML can leverage NPU on Windows 11
                ep_list = ['DmlExecutionProvider', 'CPUExecutionProvider']
            else:
                logger.warning("No NPU execution provider found, using CPU")
                ep_list = ['CPUExecutionProvider']

            # Session options for NPU optimization
            sess_options = ort.SessionOptions()
            sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

            # Load ONNX model
            # Note: You need to export or download NPU-optimized ONNX model
            onnx_model_path = model_dir / f"whisper-{self.model_name}-npu.onnx"

            if not onnx_model_path.exists():
                logger.info(f"NPU model not found at {onnx_model_path}")
                logger.info("Attempting to download/convert model...")
                self._download_or_convert_model(onnx_model_path)

            if onnx_model_path.exists():
                self.model = ort.InferenceSession(
                    str(onnx_model_path),
                    sess_options=sess_options,
                    providers=ep_list
                )
                self._is_loaded = True
                logger.info(f"Whisper NPU model loaded successfully using {ep_list[0]}")
                return True
            else:
                logger.error("Failed to load or create NPU model")
                return False

        except ImportError as e:
            logger.error(f"Missing dependencies for NPU: {e}")
            logger.info("Install with: pip install onnxruntime transformers")
            self._is_loaded = False
            return False
        except Exception as e:
            logger.error(f"Failed to load Whisper NPU model: {e}")
            self._is_loaded = False
            return False

    def _get_huggingface_model_id(self) -> str:
        """Get HuggingFace model ID based on model name."""
        model_map = {
            "base": "openai/whisper-base",
            "small": "openai/whisper-small",
            "medium": "openai/whisper-medium",
            "large": "openai/whisper-large-v3",
            "large-v3": "openai/whisper-large-v3",
        }
        return model_map.get(self.model_name, "openai/whisper-medium")

    def _download_or_convert_model(self, output_path: Path) -> bool:
        """
        Download pre-converted NPU model or convert from HuggingFace.

        For production, you should use pre-converted models from:
        - amd/NPU-Whisper-Base-Small
        - magicunicorn/whisper-medium-amd-npu-int8
        """
        try:
            # Try to download pre-converted model from HuggingFace
            from huggingface_hub import hf_hub_download

            npu_model_map = {
                "base": "amd/NPU-Whisper-Base-Small",
                "small": "amd/NPU-Whisper-Base-Small",
                "medium": "magicunicorn/whisper-medium-amd-npu-int8",
                "large": "magicunicorn/whisper-large-v3-amd-npu-int8",
                "large-v3": "magicunicorn/whisper-large-v3-amd-npu-int8",
            }

            repo_id = npu_model_map.get(self.model_name)
            if repo_id:
                logger.info(f"Downloading NPU model from {repo_id}")
                # Note: Actual file name may vary
                downloaded = hf_hub_download(
                    repo_id=repo_id,
                    filename="model.onnx",
                    cache_dir=str(output_path.parent)
                )
                # Copy or link to expected location
                import shutil
                shutil.copy(downloaded, output_path)
                logger.info(f"NPU model downloaded to {output_path}")
                return True

        except Exception as e:
            logger.warning(f"Could not download pre-converted model: {e}")

        logger.warning(
            "NPU model not available. For best performance, install AMD Ryzen AI SDK "
            "and use pre-converted models from HuggingFace."
        )
        return False

    def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None,
    ) -> NPUTranscriptionResult:
        """
        Transcribe an audio file using NPU.

        Args:
            audio_path: Path to the audio file
            language: Language code (None for auto-detect)

        Returns:
            NPUTranscriptionResult with full text and segments
        """
        if not self._is_loaded:
            if not self.load_model():
                raise RuntimeError("Failed to load Whisper NPU model")

        # Validate file exists
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        logger.info(f"Transcribing with NPU: {audio_path}")

        try:
            import librosa
            import numpy as np

            # Load and preprocess audio
            audio, sr = librosa.load(audio_path, sr=16000)
            duration = len(audio) / sr

            # Process audio for Whisper
            inputs = self.processor(
                audio,
                sampling_rate=16000,
                return_tensors="np"
            )

            # Run inference on NPU
            input_features = inputs.input_features
            outputs = self.model.run(None, {"input_features": input_features})

            # Decode outputs
            predicted_ids = np.argmax(outputs[0], axis=-1)
            transcription = self.processor.batch_decode(
                predicted_ids,
                skip_special_tokens=True
            )[0]

            # Detect language with code-switching support
            # If user specified a language (not "auto" or "bilingual"), use it
            # Otherwise, detect from transcribed text
            if language and language not in ("auto", "bilingual", None):
                detected_language = language
                language_confidence = 1.0
                is_code_switched = False
            else:
                # Auto-detect from transcribed text (supports bilingual detection)
                detected_language, language_confidence, is_code_switched = \
                    self._detect_language_from_text(transcription)

            # Create segment with language metadata
            segment = NPUTranscriptionSegment(
                start=0.0,
                end=duration,
                text=transcription.strip(),
                words=[],
                language_detected=detected_language,
                language_confidence=language_confidence,
                is_code_switched=is_code_switched
            )

            result = NPUTranscriptionResult(
                text=transcription.strip(),
                segments=[segment],
                language=detected_language,
                language_probability=language_confidence,
                duration=duration,
                device="npu"
            )

            logger.info(
                f"NPU transcription complete: {len(transcription)} chars, "
                f"language={detected_language} (confidence={language_confidence:.2f}, "
                f"code_switched={is_code_switched})"
            )
            return result

        except Exception as e:
            logger.error(f"NPU transcription failed: {e}")
            raise

    def _detect_language_from_text(self, text: str) -> tuple[str, float, bool]:
        """
        Detect language from transcribed text with code-switching support.

        Returns:
            Tuple of (language_code, confidence, is_code_switched)
            - language_code: 'fr', 'en', 'bilingual', or 'auto'
            - confidence: 0.0 to 1.0
            - is_code_switched: True if both languages detected
        """
        # Extended indicators for better detection
        french_indicators = {
            "le", "la", "les", "de", "du", "des", "et", "est", "en", "un", "une",
            "que", "qui", "je", "tu", "il", "elle", "nous", "vous", "ils", "elles",
            "ce", "cette", "ces", "mon", "ma", "mes", "ton", "ta", "tes", "son", "sa", "ses",
            "pour", "dans", "sur", "avec", "par", "mais", "ou", "donc", "car", "ni",
            "pas", "ne", "plus", "moins", "très", "bien", "mal", "oui", "non",
            "faire", "avoir", "être", "aller", "venir", "voir", "dire", "prendre",
            "c'est", "qu'est-ce", "pourquoi", "comment", "quand", "où"
        }
        english_indicators = {
            "the", "a", "an", "is", "are", "was", "were", "and", "or", "to", "of",
            "in", "it", "that", "this", "i", "you", "he", "she", "we", "they",
            "my", "your", "his", "her", "our", "their", "what", "which", "who",
            "for", "on", "with", "by", "but", "so", "because", "if", "then",
            "not", "no", "yes", "very", "well", "good", "bad", "much", "many",
            "have", "has", "had", "do", "does", "did", "will", "would", "can", "could",
            "it's", "don't", "doesn't", "didn't", "won't", "can't", "couldn't",
            "what's", "that's", "there's", "here's", "let's"
        }

        text_lower = text.lower()
        # Handle contractions and punctuation
        words = text_lower.replace("'", " ").replace("'", " ").split()

        french_count = sum(1 for w in words if w in french_indicators)
        english_count = sum(1 for w in words if w in english_indicators)
        total_indicators = french_count + english_count

        # Calculate confidence based on indicator density
        total_words = len(words)
        if total_words == 0:
            return "auto", 0.0, False

        # Detect code-switching: both languages have significant presence
        fr_ratio = french_count / total_words if total_words > 0 else 0
        en_ratio = english_count / total_words if total_words > 0 else 0

        # Thresholds for code-switching detection
        # If both languages have at least 10% indicator presence, it's bilingual
        is_code_switched = fr_ratio >= 0.05 and en_ratio >= 0.05

        if is_code_switched:
            # Both languages detected significantly
            confidence = min(fr_ratio + en_ratio, 1.0)
            return "bilingual", confidence, True
        elif french_count > english_count:
            confidence = fr_ratio / (fr_ratio + en_ratio) if total_indicators > 0 else 0.5
            return "fr", confidence, False
        elif english_count > french_count:
            confidence = en_ratio / (fr_ratio + en_ratio) if total_indicators > 0 else 0.5
            return "en", confidence, False
        else:
            return "auto", 0.5, False

    def unload_model(self):
        """Unload the model to free memory."""
        if self.model is not None:
            del self.model
            self.model = None
        if self.processor is not None:
            del self.processor
            self.processor = None
        self._is_loaded = False

        import gc
        gc.collect()

        logger.info("Whisper NPU model unloaded")


# Singleton instance
_npu_service: Optional[NPUWhisperService] = None


def get_npu_whisper_service() -> NPUWhisperService:
    """Get the singleton NPU Whisper service instance."""
    global _npu_service
    if _npu_service is None:
        _npu_service = NPUWhisperService()
    return _npu_service
