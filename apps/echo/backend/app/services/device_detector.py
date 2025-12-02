"""
Device detection service for Whisper transcription.

Detects available hardware accelerators (NPU, GPU, CPU) and provides
device information for the settings UI.
"""

import logging
import platform
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DeviceInfo:
    """Information about a compute device."""
    name: str
    type: str  # 'npu', 'gpu', 'cpu'
    status: str  # 'available', 'unavailable', 'error'
    details: Optional[str] = None


class DeviceDetector:
    """
    Detects available compute devices for Whisper transcription.

    Priority order: NPU > GPU > CPU
    """

    _instance: Optional['DeviceDetector'] = None
    _cache: Optional[Dict[str, Any]] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._cache = None

    def _check_npu(self) -> DeviceInfo:
        """Check for AMD Ryzen AI NPU availability."""
        try:
            import onnxruntime as ort
            providers = ort.get_available_providers()

            if 'VitisAIExecutionProvider' in providers:
                logger.info("AMD VitisAI NPU detected")
                return DeviceInfo(
                    name="AMD Ryzen AI NPU",
                    type="npu",
                    status="available",
                    details="VitisAI Execution Provider active"
                )
            else:
                return DeviceInfo(
                    name="AMD Ryzen AI NPU",
                    type="npu",
                    status="unavailable",
                    details="VitisAI EP not found. Install Ryzen AI SDK."
                )
        except ImportError:
            return DeviceInfo(
                name="AMD Ryzen AI NPU",
                type="npu",
                status="unavailable",
                details="onnxruntime not installed"
            )
        except Exception as e:
            logger.debug(f"NPU check error: {e}")
            return DeviceInfo(
                name="AMD Ryzen AI NPU",
                type="npu",
                status="error",
                details=str(e)
            )

    def _check_gpu(self) -> DeviceInfo:
        """Check for CUDA GPU availability."""
        try:
            import torch
            if torch.cuda.is_available():
                gpu_name = torch.cuda.get_device_name(0)
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                logger.info(f"CUDA GPU detected: {gpu_name}")
                return DeviceInfo(
                    name=gpu_name,
                    type="gpu",
                    status="available",
                    details=f"{gpu_memory:.1f}GB VRAM"
                )
            else:
                return DeviceInfo(
                    name="CUDA GPU",
                    type="gpu",
                    status="unavailable",
                    details="CUDA not available"
                )
        except ImportError:
            return DeviceInfo(
                name="CUDA GPU",
                type="gpu",
                status="unavailable",
                details="PyTorch not installed"
            )
        except Exception as e:
            logger.debug(f"GPU check error: {e}")
            return DeviceInfo(
                name="CUDA GPU",
                type="gpu",
                status="error",
                details=str(e)
            )

    def _check_cpu(self) -> DeviceInfo:
        """Get CPU information."""
        try:
            cpu_name = platform.processor() or "Unknown CPU"
            # Try to get more detailed CPU info on Windows
            if platform.system() == "Windows":
                try:
                    import subprocess
                    result = subprocess.run(
                        ['wmic', 'cpu', 'get', 'name'],
                        capture_output=True, text=True, timeout=5
                    )
                    lines = [l.strip() for l in result.stdout.split('\n') if l.strip() and l.strip() != 'Name']
                    if lines:
                        cpu_name = lines[0]
                except Exception:
                    pass

            return DeviceInfo(
                name=cpu_name,
                type="cpu",
                status="available",
                details="Always available"
            )
        except Exception as e:
            return DeviceInfo(
                name="CPU",
                type="cpu",
                status="available",
                details=str(e)
            )

    def get_available_devices(self, force_refresh: bool = False) -> List[str]:
        """
        Get list of available device types.

        Returns:
            List of device types that are available (e.g., ['cpu', 'npu'])
        """
        info = self.get_device_info(force_refresh)
        return [
            device_type
            for device_type, device_info in info.items()
            if device_info.get("status") == "available"
        ]

    def get_device_info(self, force_refresh: bool = False) -> Dict[str, Dict[str, Any]]:
        """
        Get detailed information about all devices.

        Args:
            force_refresh: Force re-detection of devices

        Returns:
            Dict with device type as key and info dict as value
        """
        if self._cache is not None and not force_refresh:
            return self._cache

        logger.info("Detecting available compute devices...")

        npu = self._check_npu()
        gpu = self._check_gpu()
        cpu = self._check_cpu()

        self._cache = {
            "cpu": {
                "name": cpu.name,
                "status": cpu.status,
                "details": cpu.details,
            },
            "gpu": {
                "name": gpu.name,
                "status": gpu.status,
                "details": gpu.details,
            },
            "npu": {
                "name": npu.name,
                "status": npu.status,
                "details": npu.details,
            },
        }

        available = self.get_available_devices()
        logger.info(f"Available devices: {available}")

        return self._cache

    def get_best_device(self) -> str:
        """
        Get the best available device (priority: NPU > GPU > CPU).

        Returns:
            Device type string ('npu', 'gpu', or 'cpu')
        """
        available = self.get_available_devices()

        # Priority order
        for device in ['npu', 'gpu', 'cpu']:
            if device in available:
                return device

        # Fallback
        return 'cpu'

    def resolve_device(self, requested_device: str) -> str:
        """
        Resolve the actual device to use based on requested device.

        Args:
            requested_device: 'auto', 'npu', 'gpu', or 'cpu'

        Returns:
            Actual device type to use
        """
        if requested_device == 'auto':
            return self.get_best_device()

        available = self.get_available_devices()
        if requested_device in available:
            return requested_device

        # Fallback to best available
        logger.warning(
            f"Requested device '{requested_device}' not available. "
            f"Falling back to '{self.get_best_device()}'"
        )
        return self.get_best_device()


# Singleton instance
_detector: Optional[DeviceDetector] = None


def get_device_detector() -> DeviceDetector:
    """Get the singleton device detector instance."""
    global _detector
    if _detector is None:
        _detector = DeviceDetector()
    return _detector


def get_available_devices() -> List[str]:
    """Get list of available device types."""
    return get_device_detector().get_available_devices()


def get_device_info() -> Dict[str, Dict[str, Any]]:
    """Get detailed device information."""
    return get_device_detector().get_device_info()


def get_active_device(requested: str = "auto") -> str:
    """Get the device that will be used for transcription."""
    return get_device_detector().resolve_device(requested)
