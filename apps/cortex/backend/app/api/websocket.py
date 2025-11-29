"""
WebSocket API

Real-time communication for task progress and agent updates.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections for sessions."""

    def __init__(self):
        # session_id -> set of websocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        """Accept and register a new connection."""
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = set()
        self.active_connections[session_id].add(websocket)

    def disconnect(self, websocket: WebSocket, session_id: str):
        """Remove a connection."""
        if session_id in self.active_connections:
            self.active_connections[session_id].discard(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]

    async def broadcast_to_session(self, session_id: str, message: dict):
        """Broadcast a message to all connections in a session."""
        if session_id in self.active_connections:
            for connection in self.active_connections[session_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    # Connection might be closed
                    pass


manager = ConnectionManager()


@router.websocket("/sessions/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time session updates.

    Message types:
    - task_started: Task execution started
    - task_progress: Task progress update (iteration, thinking, action)
    - task_completed: Task completed successfully
    - task_failed: Task failed with error
    - context_updated: Context was modified
    - file_modified: A file was modified by the agent
    """
    await manager.connect(websocket, session_id)

    try:
        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "session_id": session_id,
            "message": "Connected to CORTEX session"
        })

        while True:
            # Receive messages from client
            data = await websocket.receive_text()
            message = json.loads(data)

            # Handle client messages
            if message.get("type") == "ping":
                await websocket.send_json({"type": "pong"})

            elif message.get("type") == "subscribe":
                # Client wants to subscribe to specific events
                await websocket.send_json({
                    "type": "subscribed",
                    "events": message.get("events", ["all"])
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)


async def notify_task_progress(session_id: str, task_id: str, progress: dict):
    """Helper to notify all session connections about task progress."""
    await manager.broadcast_to_session(session_id, {
        "type": "task_progress",
        "task_id": task_id,
        **progress
    })


async def notify_file_modified(session_id: str, file_path: str, action: str):
    """Helper to notify about file modifications."""
    await manager.broadcast_to_session(session_id, {
        "type": "file_modified",
        "file_path": file_path,
        "action": action  # "read", "write", "edit"
    })
