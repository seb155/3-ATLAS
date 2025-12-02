"""
AMD Ryzen AI NPU Whisper transcription service.

Provides NPU-accelerated speech-to-text using AMD Ryzen AI SDK with
separate encoder/decoder ONNX models optimized for the XDNA NPU.

Architecture:
    Audio → Feature Extraction → Encoder (NPU) → Decoder (NPU) → Text

Requirements:
- AMD Ryzen AI SDK 1.6.1+
- NPU Driver MCDM v32.0.203.280+
- Windows 11
- onnxruntime with VitisAI EP

Supported models (from HuggingFace):
- amd/whisper-small-onnx-npu
- amd/whisper-medium-onnx-npu
- amd/whisper-large-turbo-onnx-npu
"""

import logging
import time
import json
from typing import Optional, List, Tuple
from dataclasses import dataclass
from pathlib import Path
import os

from ..config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# Constants
SAMPLE_RATE = 16000
MAX_DECODE_LENGTH = 448  # Fixed decoder sequence length


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
    rtf: float = 0.0  # Real-time factor


class WhisperONNXModel:
    """
    Whisper ONNX model with separate encoder and decoder.

    Based on AMD's reference implementation for Ryzen AI NPU.
    """

    def __init__(
        self,
        encoder_path: str,
        decoder_path: str,
        model_type: str,
        encoder_providers: Optional[list] = None,
        decoder_providers: Optional[list] = None
    ):
        import onnxruntime as ort
        from transformers import WhisperFeatureExtractor, WhisperTokenizer

        logger.info(f"Loading Whisper ONNX encoder: {encoder_path}")
        self.encoder = ort.InferenceSession(encoder_path, providers=encoder_providers)

        logger.info(f"Loading Whisper ONNX decoder: {decoder_path}")
        self.decoder = ort.InferenceSession(decoder_path, providers=decoder_providers)

        # Load tokenizer and feature extractor
        self.feature_extractor = WhisperFeatureExtractor.from_pretrained(f"openai/{model_type}")
        self.tokenizer = WhisperTokenizer.from_pretrained(f"openai/{model_type}")

        # Special tokens
        self.sot_token = self.tokenizer.convert_tokens_to_ids("<|startoftranscript|>")
        self.eos_token = self.tokenizer.eos_token_id

        # Get max length from decoder input shape
        decoder_input_shape = self.decoder.get_inputs()[0].shape[1]
        self.max_length = min(MAX_DECODE_LENGTH, decoder_input_shape) if isinstance(decoder_input_shape, int) else MAX_DECODE_LENGTH

        logger.info(f"Whisper ONNX model loaded: max_length={self.max_length}")

    def preprocess(self, audio) -> "np.ndarray":
        """Convert raw audio to Whisper log-mel spectrogram."""
        import numpy as np
        inputs = self.feature_extractor(audio, sampling_rate=SAMPLE_RATE, return_tensors="np")
        return inputs["input_features"].astype(np.float32)

    def encode(self, input_features: "np.ndarray") -> "np.ndarray":
        """Run encoder ONNX model."""
        return self.encoder.run(None, {"x": input_features})[0]

    def decode(self, encoder_out: "np.ndarray") -> Tuple[List[int], Optional[float]]:
        """
        Greedy decode with fixed-length input_ids.

        Returns:
            Tuple of (token_ids, time_to_first_token)
        """
        import numpy as np

        tokens = [self.sot_token]
        first_token_time = None
        decode_start = time.time()

        for _ in range(self.max_length):
            # Pad to fixed length
            decoder_input = np.full((1, self.max_length), self.eos_token, dtype=np.int64)
            decoder_input[0, :len(tokens)] = tokens

            # Run decoder
            outputs = self.decoder.run(None, {
                "x": decoder_input,
                "xa": encoder_out
            })

            # Get next token (greedy)
            logits = outputs[0]
            next_token = int(np.argmax(logits[0, len(tokens) - 1]))

            if first_token_time is None:
                first_token_time = time.time() - decode_start

            if next_token == self.eos_token:
                break

            tokens.append(next_token)

        return tokens, first_token_time

    def transcribe(self, audio, chunk_length_s: int = 30) -> Tuple[str, float]:
        """
        Full encode-decode pipeline with chunking for long audio.

        Args:
            audio: Audio samples as numpy array (16kHz mono float32)
            chunk_length_s: Chunk length in seconds for long audio

        Returns:
            Tuple of (transcription_text, real_time_factor)
        """
        import numpy as np

        chunk_size = SAMPLE_RATE * chunk_length_s
        total_samples = len(audio)
        transcription_parts = []

        total_start = time.time()
        overlap = SAMPLE_RATE * 1  # 1 second overlap between chunks

        for start in range(0, total_samples, chunk_size - overlap):
            end = min(start + chunk_size, total_samples)
            audio_chunk = audio[start:end]

            # Encode
            input_features = self.preprocess(audio_chunk)
            encoder_out = self.encode(input_features)

            # Decode
            tokens, _ = self.decode(encoder_out)
            text = self.tokenizer.decode(tokens, skip_special_tokens=True).strip()
            transcription_parts.append(text)

        total_time = time.time() - total_start
        audio_duration = total_samples / SAMPLE_RATE
        rtf = total_time / audio_duration if audio_duration > 0 else 0

        return " ".join(transcription_parts), rtf


class NPUWhisperService:
    """
    AMD Ryzen AI NPU Whisper transcription service.

    Uses the Ryzen AI SDK for NPU-accelerated inference with separate
    encoder and decoder ONNX models.

    Features:
    - NPU acceleration (50 TOPS on Ryzen AI 9 HX 370)
    - French Canadian and English support
    - Auto language detection
    - Bilingual/code-switching detection
    - Energy-efficient processing
    """

    # HuggingFace model repos
    HF_MODEL_MAP = {
        "small": "amd/whisper-small-onnx-npu",
        "medium": "amd/whisper-medium-onnx-npu",
        "large-v3-turbo": "amd/whisper-large-turbo-onnx-npu",
    }

    # OpenAI model names for tokenizer
    OPENAI_MODEL_MAP = {
        "small": "whisper-small",
        "medium": "whisper-medium",
        "large-v3-turbo": "whisper-large-v3",
    }

    def __init__(self):
        self.model: Optional[WhisperONNXModel] = None
        self.model_name = getattr(settings, 'whisper_model_npu', 'medium')
        self._is_loaded = False
        self._npu_available = None
        self._model_dir: Optional[Path] = None

    @staticmethod
    def is_npu_available() -> bool:
        """
        Check if AMD Ryzen AI NPU is available.

        Returns:
            True if VitisAI Execution Provider is available
        """
        try:
            import onnxruntime as ort
            providers = ort.get_available_providers()

            if 'VitisAIExecutionProvider' in providers:
                logger.info("AMD VitisAI Execution Provider detected - NPU available")
                return True

            logger.debug(f"Available ONNX providers: {providers}")
            logger.debug("VitisAIExecutionProvider not found - NPU not available")
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

    def _get_model_dir(self) -> Path:
        """Get or create the model directory."""
        if self._model_dir is None:
            base_path = Path(settings.audio_storage_path) / "models" / "npu"
            base_path.mkdir(parents=True, exist_ok=True)
            self._model_dir = base_path
        return self._model_dir

    def _get_config_dir(self) -> Path:
        """Get or create the VitisAI config directory."""
        config_dir = self._get_model_dir() / "config"
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir

    def _ensure_vitisai_configs(self) -> Tuple[Path, Path]:
        """
        Ensure VitisAI config files exist for encoder and decoder.

        Returns:
            Tuple of (encoder_config_path, decoder_config_path)
        """
        config_dir = self._get_config_dir()

        encoder_config = config_dir / "vitisai_config_encoder.json"
        decoder_config = config_dir / "vitisai_config_decoder.json"

        # Encoder config (with accurate mode for LayerNorm)
        encoder_config_data = {
            "passes": [
                {"name": "init", "plugin": "vaip-pass_init"},
                {
                    "name": "vaiml_partition",
                    "plugin": "vaip-pass_vaiml_partition",
                    "vaiml_config": {
                        "optimize_level": 3,
                        "fe_experiment": "use-accurate-mode=LayerNorm2PassAdf",
                        "aiecompiler_args": "--system-stack-size=512"
                    }
                }
            ],
            "target": "VAIML",
            "targets": [{"name": "VAIML", "pass": ["init", "vaiml_partition"]}]
        }

        # Decoder config
        decoder_config_data = {
            "passes": [
                {"name": "init", "plugin": "vaip-pass_init"},
                {
                    "name": "vaiml_partition",
                    "plugin": "vaip-pass_vaiml_partition",
                    "vaiml_config": {
                        "optimize_level": 3,
                        "aiecompiler_args": "--system-stack-size=512"
                    }
                }
            ],
            "target": "VAIML",
            "targets": [{"name": "VAIML", "pass": ["init", "vaiml_partition"]}]
        }

        # Write configs if they don't exist
        if not encoder_config.exists():
            with open(encoder_config, 'w') as f:
                json.dump(encoder_config_data, f, indent=2)
            logger.info(f"Created VitisAI encoder config: {encoder_config}")

        if not decoder_config.exists():
            with open(decoder_config, 'w') as f:
                json.dump(decoder_config_data, f, indent=2)
            logger.info(f"Created VitisAI decoder config: {decoder_config}")

        return encoder_config, decoder_config

    def _download_model(self) -> Tuple[Path, Path]:
        """
        Download Whisper ONNX model from HuggingFace.

        Returns:
            Tuple of (encoder_path, decoder_path)
        """
        from huggingface_hub import snapshot_download

        # Map model name to HF repo
        model_key = self.model_name.lower()
        if model_key not in self.HF_MODEL_MAP:
            # Default to medium if unknown
            logger.warning(f"Unknown model '{model_key}', defaulting to 'medium'")
            model_key = "medium"

        repo_id = self.HF_MODEL_MAP[model_key]
        logger.info(f"Downloading Whisper ONNX model from {repo_id}...")

        # Download entire repo
        local_dir = snapshot_download(
            repo_id=repo_id,
            cache_dir=str(self._get_model_dir() / ".cache")
        )

        # Find encoder and decoder files
        local_path = Path(local_dir)
        encoder_path = local_path / "encoder_model.onnx"
        decoder_path = local_path / "decoder_model.onnx"

        if not encoder_path.exists():
            raise FileNotFoundError(f"Encoder not found at {encoder_path}")
        if not decoder_path.exists():
            raise FileNotFoundError(f"Decoder not found at {decoder_path}")

        logger.info(f"Model downloaded: encoder={encoder_path}, decoder={decoder_path}")
        return encoder_path, decoder_path

    def _build_provider_options(self, config_path: Path, cache_key: str) -> list:
        """
        Build ONNX Runtime provider options for VitisAI EP.

        Args:
            config_path: Path to VitisAI config JSON
            cache_key: Unique key for caching compiled model

        Returns:
            List of provider options for ort.InferenceSession
        """
        cache_dir = str(self._get_model_dir() / "cache")
        os.makedirs(cache_dir, exist_ok=True)

        return [
            (
                "VitisAIExecutionProvider",
                {
                    "config_file": str(config_path),
                    "cache_dir": cache_dir,
                    "cache_key": cache_key
                }
            ),
            "CPUExecutionProvider"  # Fallback
        ]

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
            # Check NPU availability
            if not self.is_npu_available():
                logger.warning("NPU not available, cannot load NPU model")
                return False

            # Download model if needed
            encoder_path, decoder_path = self._download_model()

            # Ensure VitisAI configs exist
            encoder_config, decoder_config = self._ensure_vitisai_configs()

            # Build provider options
            model_key = self.model_name.lower()
            encoder_providers = self._build_provider_options(
                encoder_config,
                f"whisper_{model_key}_encoder"
            )
            decoder_providers = self._build_provider_options(
                decoder_config,
                f"whisper_{model_key}_decoder"
            )

            # Get OpenAI model name for tokenizer
            openai_model = self.OPENAI_MODEL_MAP.get(model_key, "whisper-medium")

            logger.info(f"Loading Whisper ONNX model with VitisAI EP...")
            logger.info("Note: First load may take several minutes for NPU compilation")

            self.model = WhisperONNXModel(
                encoder_path=str(encoder_path),
                decoder_path=str(decoder_path),
                model_type=openai_model,
                encoder_providers=encoder_providers,
                decoder_providers=decoder_providers
            )

            self._is_loaded = True
            logger.info(f"Whisper NPU model '{self.model_name}' loaded successfully")
            return True

        except ImportError as e:
            logger.error(f"Missing dependencies for NPU: {e}")
            logger.info("Install with: pip install onnxruntime transformers huggingface_hub")
            self._is_loaded = False
            return False
        except Exception as e:
            logger.error(f"Failed to load Whisper NPU model: {e}")
            self._is_loaded = False
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

        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        logger.info(f"Transcribing with NPU: {audio_path}")

        try:
            import librosa
            import numpy as np

            # Load and preprocess audio
            start_time = time.time()
            audio, sr = librosa.load(audio_path, sr=SAMPLE_RATE)
            duration = len(audio) / sr

            logger.debug(f"Audio loaded: {duration:.2f}s, {len(audio)} samples")

            # Run transcription
            transcription, rtf = self.model.transcribe(audio)

            elapsed = time.time() - start_time

            # Detect language with code-switching support
            if language and language not in ("auto", "bilingual", None):
                detected_language = language
                language_confidence = 1.0
                is_code_switched = False
            else:
                detected_language, language_confidence, is_code_switched = \
                    self._detect_language_from_text(transcription)

            # Create segment (single segment for now, chunked audio combined)
            segment = NPUTranscriptionSegment(
                start=0.0,
                end=duration,
                text=transcription.strip(),
                words=[],  # Word timestamps not available in basic ONNX mode
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
                device="npu",
                rtf=rtf
            )

            logger.info(
                f"NPU transcription complete: {len(transcription)} chars, "
                f"duration={duration:.2f}s, elapsed={elapsed:.2f}s, rtf={rtf:.3f}, "
                f"language={detected_language} (conf={language_confidence:.2f}, "
                f"code_switched={is_code_switched})"
            )

            return result

        except Exception as e:
            logger.error(f"NPU transcription failed: {e}")
            raise

    def _detect_language_from_text(self, text: str) -> Tuple[str, float, bool]:
        """
        Detect language from transcribed text with code-switching support.

        Returns:
            Tuple of (language_code, confidence, is_code_switched)
        """
        # Extended indicators for French Canadian and English
        french_indicators = {
            "le", "la", "les", "de", "du", "des", "et", "est", "en", "un", "une",
            "que", "qui", "je", "tu", "il", "elle", "nous", "vous", "ils", "elles",
            "ce", "cette", "ces", "mon", "ma", "mes", "ton", "ta", "tes", "son", "sa", "ses",
            "pour", "dans", "sur", "avec", "par", "mais", "ou", "donc", "car", "ni",
            "pas", "ne", "plus", "moins", "tres", "bien", "mal", "oui", "non",
            "faire", "avoir", "etre", "aller", "venir", "voir", "dire", "prendre",
            "c'est", "qu'est-ce", "pourquoi", "comment", "quand", "ou",
            # Quebec French specifics
            "pis", "ben", "faque", "tsé", "la", "icitte", "pantoute", "tiguidou"
        }

        english_indicators = {
            "the", "a", "an", "is", "are", "was", "were", "and", "or", "to", "of",
            "in", "it", "that", "this", "i", "you", "he", "she", "we", "they",
            "my", "your", "his", "her", "our", "their", "what", "which", "who",
            "for", "on", "with", "by", "but", "so", "because", "if", "then",
            "not", "no", "yes", "very", "well", "good", "bad", "much", "many",
            "have", "has", "had", "do", "does", "did", "will", "would", "can", "could",
            "it's", "don't", "doesn't", "didn't", "won't", "can't", "couldn't",
            "what's", "that's", "there's", "here's", "let's",
            "yeah", "okay", "ok", "alright"
        }

        text_lower = text.lower()
        words = text_lower.replace("'", " ").replace("'", " ").split()

        french_count = sum(1 for w in words if w in french_indicators)
        english_count = sum(1 for w in words if w in english_indicators)
        total_words = len(words)

        if total_words == 0:
            return "auto", 0.0, False

        fr_ratio = french_count / total_words
        en_ratio = english_count / total_words

        # Code-switching: both languages have significant presence
        # Threshold raised from 5% to 15% to reduce false positives
        # (e.g., a single "meeting" or "email" in French speech)
        is_code_switched = fr_ratio >= 0.15 and en_ratio >= 0.15

        if is_code_switched:
            confidence = min(fr_ratio + en_ratio, 1.0)
            return "bilingual", confidence, True
        elif french_count > english_count:
            total_indicators = french_count + english_count
            confidence = fr_ratio / (fr_ratio + en_ratio) if total_indicators > 0 else 0.5
            return "fr", confidence, False
        elif english_count > french_count:
            total_indicators = french_count + english_count
            confidence = en_ratio / (fr_ratio + en_ratio) if total_indicators > 0 else 0.5
            return "en", confidence, False
        else:
            return "auto", 0.5, False

    def unload_model(self):
        """Unload the model to free memory."""
        if self.model is not None:
            del self.model
            self.model = None

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
