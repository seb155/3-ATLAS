"""
WebSocket endpoint for real-time log streaming.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.websocket_manager import WebSocketLogger, log_manager

router = APIRouter()


@router.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    """
    WebSocket endpoint for real-time log streaming.
    Connect from frontend DevConsole to receive logs in real-time.
    """
    await log_manager.connect(websocket)

    # Send recent logs on connect
    recent_logs = WebSocketLogger.get_logs(limit=50)
    for log in recent_logs:
        try:
            await websocket.send_json(log)
        except Exception:
            break

    try:
        while True:
            # Keep connection alive, handle incoming messages
            data = await websocket.receive_text()
            # Can handle commands from frontend if needed
            if data == "ping":
                await websocket.send_text("pong")
            elif data == "clear":
                WebSocketLogger.clear()
    except WebSocketDisconnect:
        log_manager.disconnect(websocket)
    except Exception:
        log_manager.disconnect(websocket)


@router.get("/api/v1/logs/")
async def get_logs(limit: int = 100):
    """
    HTTP endpoint for fetching logs (fallback for non-WebSocket clients).
    """
    return WebSocketLogger.get_logs(limit=limit)


@router.delete("/api/v1/logs/")
async def clear_logs():
    """Clear all logs."""
    WebSocketLogger.clear()
    return {"status": "cleared"}


@router.get("/api/v1/logs/connections")
async def get_connection_count():
    """Get number of active WebSocket connections."""
    return {"connections": log_manager.connection_count}
