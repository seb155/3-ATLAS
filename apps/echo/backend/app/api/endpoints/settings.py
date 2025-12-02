"""
Settings endpoints for Whisper model and device configuration.

Provides API to:
- View current Whisper settings
- Change model and device
- Get available devices and their status
"""

import logging
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ...config import get_settings, WHISPER_MODELS, WHISPER_DEVICES
from ...services.device_detector import (
    get_device_detector,
    get_available_devices,
    get_device_info,
    get_active_device,
)
from ...services.transcription_service import get_transcription_service

router = APIRouter()
settings = get_settings()
logger = logging.getLogger(__name__)


class WhisperModelInfo(BaseModel):
    """Information about a Whisper model."""
    name: str
    size: str
    vram: str
    speed: str
    quality: str


class DeviceStatus(BaseModel):
    """Status of a compute device."""
    name: str
    status: str  # 'available', 'unavailable', 'error'
    details: Optional[str] = None


class WhisperSettingsResponse(BaseModel):
    """Response for GET /settings/whisper."""
    # Current configuration
    model: str
    device: str  # Configured device preference

    # Active state
    active_device: str  # Actually being used
    model_loaded: bool

    # Available options
    available_models: List[WhisperModelInfo]
    available_devices: List[str]

    # Device details
    device_info: Dict[str, DeviceStatus]


class WhisperSettingsUpdate(BaseModel):
    """Request body for POST /settings/whisper."""
    model: Optional[str] = None
    device: Optional[str] = None


class WhisperSettingsUpdateResponse(BaseModel):
    """Response for POST /settings/whisper."""
    success: bool
    message: str
    model: str
    device: str
    active_device: str
    reload_required: bool


@router.get("/settings/whisper", response_model=WhisperSettingsResponse)
async def get_whisper_settings():
    """
    Get current Whisper transcription settings.

    Returns:
        - Current model and device configuration
        - Active device being used
        - Available models with their characteristics
        - Available devices and their status
    """
    # Get device information
    device_info_raw = get_device_info()
    device_info = {
        k: DeviceStatus(
            name=v["name"],
            status=v["status"],
            details=v.get("details")
        )
        for k, v in device_info_raw.items()
    }

    # Get available devices
    available = get_available_devices()

    # Get active device (what will actually be used)
    active_device = get_active_device(settings.whisper_device)

    # Check if model is loaded
    try:
        transcription_service = get_transcription_service()
        model_loaded = transcription_service._is_initialized
    except Exception:
        model_loaded = False

    # Build model list
    available_models = [
        WhisperModelInfo(
            name=name,
            size=info["size"],
            vram=info["vram"],
            speed=info["speed"],
            quality=info["quality"],
        )
        for name, info in WHISPER_MODELS.items()
    ]

    return WhisperSettingsResponse(
        model=settings.whisper_model,
        device=settings.whisper_device,
        active_device=active_device,
        model_loaded=model_loaded,
        available_models=available_models,
        available_devices=available,
        device_info=device_info,
    )


@router.post("/settings/whisper", response_model=WhisperSettingsUpdateResponse)
async def update_whisper_settings(update: WhisperSettingsUpdate):
    """
    Update Whisper transcription settings.

    Note: Changes are applied at runtime but not persisted.
    For persistent changes, update environment variables.

    Args:
        update: New model and/or device settings

    Returns:
        Updated settings and whether reload is required
    """
    reload_required = False
    messages = []

    # Validate and update model
    if update.model is not None:
        if update.model not in WHISPER_MODELS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid model '{update.model}'. Available: {list(WHISPER_MODELS.keys())}"
            )

        if update.model != settings.whisper_model:
            old_model = settings.whisper_model
            settings.whisper_model = update.model
            reload_required = True
            messages.append(f"Model changed from '{old_model}' to '{update.model}'")
            logger.info(f"Whisper model changed: {old_model} -> {update.model}")

    # Validate and update device
    if update.device is not None:
        if update.device not in WHISPER_DEVICES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid device '{update.device}'. Available: {WHISPER_DEVICES}"
            )

        if update.device != settings.whisper_device:
            old_device = settings.whisper_device
            settings.whisper_device = update.device
            reload_required = True
            messages.append(f"Device changed from '{old_device}' to '{update.device}'")
            logger.info(f"Whisper device changed: {old_device} -> {update.device}")

    # Reload model if needed
    if reload_required:
        try:
            transcription_service = get_transcription_service()
            # Unload current model
            transcription_service.unload()
            # The model will be reloaded on next transcription request
            messages.append("Model unloaded. Will reload on next transcription.")
            logger.info("Transcription service unloaded for settings change")
        except Exception as e:
            logger.warning(f"Could not unload transcription service: {e}")
            messages.append(f"Warning: Could not unload model: {e}")

    # Get updated active device
    active_device = get_active_device(settings.whisper_device)

    return WhisperSettingsUpdateResponse(
        success=True,
        message="; ".join(messages) if messages else "No changes made",
        model=settings.whisper_model,
        device=settings.whisper_device,
        active_device=active_device,
        reload_required=reload_required,
    )


@router.get("/settings/whisper/devices")
async def get_devices():
    """
    Get detailed information about all compute devices.

    Returns device detection results with availability status.
    """
    detector = get_device_detector()

    # Force refresh to get current state
    device_info = detector.get_device_info(force_refresh=True)
    available = detector.get_available_devices()
    best = detector.get_best_device()

    return {
        "devices": device_info,
        "available": available,
        "recommended": best,
        "current_config": settings.whisper_device,
        "active": get_active_device(settings.whisper_device),
    }


@router.post("/settings/whisper/reload")
async def reload_whisper_model():
    """
    Force reload the Whisper model.

    Useful after changing settings or if the model is in a bad state.
    """
    try:
        transcription_service = get_transcription_service()

        # Unload first
        transcription_service.unload()

        # Force reload by re-initializing
        active_device = transcription_service.initialize()

        if active_device:
            return {
                "success": True,
                "message": "Whisper model reloaded successfully",
                "device": active_device.value if hasattr(active_device, 'value') else str(active_device),
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to reload Whisper model"
            )

    except Exception as e:
        logger.error(f"Failed to reload Whisper model: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reload model: {str(e)}"
        )
