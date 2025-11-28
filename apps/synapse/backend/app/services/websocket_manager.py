"""
WebSocket Manager for real-time log streaming to DevConsole.
Manages client connections and broadcasts log entries.
"""

import asyncio
import json
from datetime import datetime
from typing import Any

from fastapi import WebSocket


class ConnectionManager:
    """Manages WebSocket connections for log streaming."""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"[WS] Client connected. Total: {len(self.active_connections)}", flush=True)

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"[WS] Client disconnected. Total: {len(self.active_connections)}", flush=True)

    async def broadcast(self, message: dict[str, Any]):
        """Broadcast a message to all connected clients."""
        if not self.active_connections:
            return

        message_json = json.dumps(message, default=str)
        disconnected = []

        for connection in self.active_connections:
            try:
                await connection.send_text(message_json)
            except Exception as e:
                print(f"[WS] Send error: {e}", flush=True)
                disconnected.append(connection)

        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(conn)

    @property
    def connection_count(self) -> int:
        """Number of active connections."""
        return len(self.active_connections)


# Global manager instance
log_manager = ConnectionManager()


class WebSocketLogger:
    """Logger that sends structured logs to both console and WebSocket clients."""

    _logs: list[dict] = []
    _max_logs = 1000

    @classmethod
    async def log(
        cls,
        level: str,
        message: str,
        source: str = "BACKEND",
        action_type: str | None = None,
        entity_id: str | None = None,
        entity_type: str | None = None,
        discipline: str | None = None,
        context: dict[str, Any] | None = None,
        parent_id: str | None = None,
        # DevConsole V3: New fields
        action_id: str | None = None,
        action_summary: str | None = None,
        action_status: str | None = None,
        action_stats: dict[str, Any] | None = None,
        user_id: str | None = None,
        user_name: str | None = None,
        topic: str | None = None,
        entity_tag: str | None = None,
        entity_route: str | None = None,
        response_time: float | None = None,
    ):
        """Log a message and broadcast to WebSocket clients."""
        import uuid

        entry = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "level": level.upper(),
            "message": message,
            "source": source,
            "actionType": action_type,
            "entityId": entity_id,
            "entityType": entity_type,
            "discipline": discipline,
            "context": context,
            "parentId": parent_id,
            "status": "COMPLETED",
            # DevConsole V3 fields
            "actionId": action_id,
            "actionSummary": action_summary,
            "actionStatus": action_status,
            "actionStats": action_stats,
            "userId": user_id,
            "userName": user_name,
            "topic": topic,
            "entityTag": entity_tag,
            "entityRoute": entity_route,
            "responseTime": response_time,
        }

        # Store locally
        cls._logs.append(entry)
        if len(cls._logs) > cls._max_logs:
            cls._logs.pop(0)

        # Print to console (for Docker logs / Promtail)
        log_json = json.dumps(
            {
                "timestamp": entry["timestamp"],
                "level": entry["level"],
                "message": entry["message"],
                "source": entry["source"],
                "action_type": entry.get("actionType"),
                "entity_id": entry.get("entityId"),
                "discipline": entry.get("discipline"),
            }
        )
        print(log_json, flush=True)

        # Broadcast to WebSocket clients
        await log_manager.broadcast(entry)

    @classmethod
    def log_sync(
        cls,
        level: str,
        message: str,
        source: str = "BACKEND",
        action_type: str | None = None,
        entity_id: str | None = None,
        entity_type: str | None = None,
        discipline: str | None = None,
        context: dict[str, Any] | None = None,
        parent_id: str | None = None,
    ):
        """Synchronous logging (for non-async contexts)."""
        import uuid

        entry = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "level": level.upper(),
            "message": message,
            "source": source,
            "actionType": action_type,
            "entityId": entity_id,
            "entityType": entity_type,
            "discipline": discipline,
            "context": context,
            "parentId": parent_id,
            "status": "COMPLETED",
        }

        # Store locally
        cls._logs.append(entry)
        if len(cls._logs) > cls._max_logs:
            cls._logs.pop(0)

        # Print to console (JSON for Promtail)
        log_json = json.dumps(
            {
                "timestamp": entry["timestamp"],
                "level": entry["level"],
                "message": entry["message"],
                "source": entry["source"],
                "action_type": entry.get("actionType"),
                "entity_id": entry.get("entityId"),
                "discipline": entry.get("discipline"),
            }
        )
        print(log_json, flush=True)

        # Queue broadcast for async execution
        try:
            # loop = asyncio.get_running_loop()
            asyncio.create_task(log_manager.broadcast(entry))
        except RuntimeError:
            pass  # No event loop, skip WebSocket broadcast

    @classmethod
    def get_logs(cls, limit: int = 100) -> list[dict]:
        """Get recent logs."""
        return cls._logs[-limit:]

    @classmethod
    def clear(cls):
        """Clear all logs."""
        cls._logs = []


# Export alias for compatibility
websocket_logger = WebSocketLogger
