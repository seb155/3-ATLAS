"""
System logger with WebSocket broadcast support.
Logs are sent to both console (for Loki/Promtail) and WebSocket clients.
"""

import json
import logging
import uuid
from datetime import datetime
from typing import Any

# Configure standard Python logging for fallback
logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger("synapse")


class SystemLog:
    """
    Backward-compatible logger that integrates with WebSocket broadcasting.
    Use WebSocketLogger for new code with full feature support.
    """

    _logs: list[dict] = []
    _max_logs = 1000

    @classmethod
    def log(
        cls,
        level: str,
        message: str,
        source: str = "BACKEND",
        action_type: str | None = None,
        entity_id: str | None = None,
        discipline: str | None = None,
        context: dict[str, Any] | None = None,
    ):
        """Log a message with optional structured metadata."""
        entry = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "level": level.upper(),
            "message": message,
            "source": source,
            "actionType": action_type,
            "entityId": entity_id,
            "discipline": discipline,
            "context": context,
            "status": "COMPLETED",
        }
        cls._logs.append(entry)
        if len(cls._logs) > cls._max_logs:
            cls._logs.pop(0)

        # JSON output for Loki/Promtail - use proper logging
        log_data = {
            "timestamp": entry["timestamp"],
            "level": entry["level"],
            "message": entry["message"],
            "source": entry["source"],
            "action_type": action_type,
            "entity_id": entity_id,
            "discipline": discipline,
        }

        # Use proper logging instead of print
        log_json = json.dumps(log_data)
        if level.upper() == "ERROR":
            _logger.error(log_json)
        elif level.upper() == "WARN":
            _logger.warning(log_json)
        elif level.upper() == "DEBUG":
            _logger.debug(log_json)
        else:
            _logger.info(log_json)

        # Try to broadcast via WebSocket
        try:
            import asyncio

            from app.services.websocket_manager import log_manager

            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(log_manager.broadcast(entry))
        except RuntimeError:
            # No event loop running - this is normal in synchronous contexts
            pass
        except ImportError:
            # WebSocket manager not available during startup
            pass
        except Exception as e:
            # Log WebSocket broadcast failure but don't crash
            _logger.warning(f"WebSocket broadcast failed: {e}")

    @classmethod
    def get_logs(cls, limit: int = 100):
        """Get recent logs."""
        return cls._logs[-limit:]

    @classmethod
    def clear(cls):
        """Clear all logs."""
        cls._logs = []

    # Convenience methods
    @classmethod
    def info(cls, message: str, **kwargs):
        cls.log("INFO", message, **kwargs)

    @classmethod
    def debug(cls, message: str, **kwargs):
        cls.log("DEBUG", message, **kwargs)

    @classmethod
    def warn(cls, message: str, **kwargs):
        cls.log("WARN", message, **kwargs)

    @classmethod
    def error(cls, message: str, **kwargs):
        cls.log("ERROR", message, **kwargs)
