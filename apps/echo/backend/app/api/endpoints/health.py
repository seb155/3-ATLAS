"""
Health check endpoints.
"""

import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any, Optional

from ...database import get_db, check_db_connection
from ...config import get_settings
from ...services.transcription_service import get_transcription_service

router = APIRouter()
settings = get_settings()
logger = logging.getLogger(__name__)


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    environment: str
    database: str
    whisper: str
    details: Dict[str, Any] = {}


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.

    Returns application health status including:
    - Database connectivity
    - Whisper model status
    - Transcription device info (NPU/GPU/CPU)
    - Environment info
    """
    # Check database
    db_status = "healthy" if check_db_connection() else "unhealthy"

    # Check transcription service
    try:
        transcription_service = get_transcription_service()
        device_info = transcription_service.device_info
        whisper_status = "loaded" if transcription_service._is_initialized else "not_loaded"
        active_device = device_info.get("active", "not_initialized")
    except Exception as e:
        logger.warning(f"Could not get transcription service info: {e}")
        whisper_status = "not_loaded"
        active_device = "unknown"
        device_info = {}

    return HealthResponse(
        status="healthy" if db_status == "healthy" else "degraded",
        version=settings.app_version,
        environment=settings.environment,
        database=db_status,
        whisper=whisper_status,
        details={
            "whisper_model_cpu": settings.whisper_model,
            "whisper_model_npu": getattr(settings, 'whisper_model_npu', 'medium'),
            "whisper_device_config": settings.whisper_device,
            "whisper_device_active": active_device,
            "npu_available": device_info.get("npu_available", False),
            "gpu_available": device_info.get("gpu_available", False),
            "audio_storage": settings.audio_storage_path,
        }
    )


@router.get("/health/ready")
async def readiness_check():
    """Kubernetes readiness probe."""
    if check_db_connection():
        return {"status": "ready"}
    return {"status": "not_ready"}, 503


@router.get("/health/live")
async def liveness_check():
    """Kubernetes liveness probe."""
    return {"status": "alive"}
