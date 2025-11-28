"""
DevConsole WebSocket & HTTP Middleware Tests

Tests for:
- WebSocket connection and broadcasting
- HTTP request logging middleware
- Log enrichment (user, topic, response time)
- Real-time log streaming
"""

import asyncio
import json
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import Request
from fastapi.responses import JSONResponse

# ============================================================================
# HTTP Middleware Logging Tests
# ============================================================================

@pytest.mark.asyncio
async def test_middleware_logs_all_requests():
    """VERIFY: Middleware logs every HTTP request"""

    from app.middleware.logging_middleware import LoggingMiddleware

    # Mock WebSocketLogger.log
    received_logs = []

    with patch("app.services.websocket_manager.websocket_logger.log", new_callable=AsyncMock) as mock_log:
        mock_log.side_effect = lambda **kwargs: received_logs.append(kwargs)

        # Mock request
        scope = {
            "type": "http",
            "method": "GET",
            "path": "/api/v1/assets",
            "headers": [],
            "query_string": b"",
        }

        async def mock_receive(): return {"type": "http.request", "body": b""}
        async def mock_send(message): pass

        request = Request(scope, mock_receive, mock_send)

        # Mock call_next
        async def mock_call_next(req):
            return JSONResponse({"status": "ok"})

        middleware = LoggingMiddleware(Mock())
        await middleware.dispatch(request, mock_call_next)

        # Verify log was called (at least twice: REQUEST and RESPONSE)
        assert len(received_logs) >= 2

        # Check first log (REQUEST)
        assert received_logs[0]["action_type"] == "REQUEST"
        assert received_logs[0]["context"]["method"] == "GET"
        assert received_logs[0]["context"]["path"] == "/api/v1/assets"

        # Check second log (RESPONSE)
        assert received_logs[1]["action_type"] == "RESPONSE"
        assert received_logs[1]["response_time"] is not None


@pytest.mark.asyncio
async def test_middleware_calculates_response_time():
    """VERIFY: Response time is calculated correctly"""
    from app.middleware.logging_middleware import LoggingMiddleware

    received_logs = []

    with patch("app.services.websocket_manager.websocket_logger.log", new_callable=AsyncMock) as mock_log:
        mock_log.side_effect = lambda **kwargs: received_logs.append(kwargs)

        # Mock slow request
        async def mock_call_next(request):
            await asyncio.sleep(0.1)
            return JSONResponse({"status": "ok"})

        scope = {
            "type": "http",
            "method": "GET",
            "path": "/api/v1/slow",
            "headers": [],
            "query_string": b"",
        }

        request = Request(scope, AsyncMock(), AsyncMock())
        middleware = LoggingMiddleware(Mock())
        await middleware.dispatch(request, mock_call_next)

        # Check response log
        response_logs = [l for l in received_logs if l.get("action_type") == "RESPONSE"]
        assert len(response_logs) == 1
        assert response_logs[0]["response_time"] >= 100


@pytest.mark.asyncio
async def test_middleware_extracts_topic_from_url():
    """VERIFY: Topic is auto-detected from URL path"""
    from app.middleware.logging_middleware import LoggingMiddleware

    test_cases = [
        ("/api/v1/assets", "ASSETS"),
        ("/api/v1/rules", "RULES"),
        ("/api/v1/cables", "CABLES"),
        ("/api/v1/projects", "PROJECT"),
        ("/api/v1/auth/login", "AUTH"),
    ]

    for path, expected_topic in test_cases:
        received_logs = []

        with patch("app.services.websocket_manager.websocket_logger.log", new_callable=AsyncMock) as mock_log:
            mock_log.side_effect = lambda **kwargs: received_logs.append(kwargs)

            async def mock_call_next(req): return JSONResponse({"status": "ok"})

            scope = {
                "type": "http",
                "method": "GET",
                "path": path,
                "headers": [],
                "query_string": b"",
            }

            request = Request(scope, AsyncMock(), AsyncMock())
            middleware = LoggingMiddleware(Mock())
            await middleware.dispatch(request, mock_call_next)

            assert received_logs[0]["topic"] == expected_topic


# ============================================================================
# WebSocket Connection Tests
# ============================================================================

@pytest.mark.asyncio
async def test_websocket_logger_formats_correctly():
    """VERIFY: WebSocket logger formats logs with all required fields"""
    from app.services.websocket_manager import WebSocketLogger, log_manager

    # Mock log_manager.broadcast
    with patch.object(log_manager, 'broadcast', new_callable=AsyncMock) as mock_broadcast:

        await WebSocketLogger.log(
            level="INFO",
            message="Test message",
            source="BACKEND",
            action_id="test-123",
            user_id="user-456"
        )

        # Verify broadcast was called with correct structure
        assert mock_broadcast.called
        call_args = mock_broadcast.call_args[0][0]

        assert call_args["level"] == "INFO"
        assert call_args["message"] == "Test message"
        assert call_args["actionId"] == "test-123"
        assert call_args["userId"] == "user-456"
        assert "timestamp" in call_args
        assert "id" in call_args


@pytest.mark.asyncio
async def test_websocket_handles_multiple_clients():
    """VERIFY: WebSocket can handle multiple connected clients"""
    from app.services.websocket_manager import ConnectionManager

    manager = ConnectionManager()

    # Simulate multiple client connections
    mock_ws1 = AsyncMock()
    mock_ws2 = AsyncMock()
    mock_ws3 = AsyncMock()

    await manager.connect(mock_ws1)
    await manager.connect(mock_ws2)
    await manager.connect(mock_ws3)

    assert len(manager.active_connections) == 3

    # Broadcast to all
    test_message = {"test": "message"}
    await manager.broadcast(test_message)

    # Verify all clients received message
    # Note: broadcast calls send_text with JSON string
    expected_json = json.dumps(test_message)
    mock_ws1.send_text.assert_called_once()
    mock_ws2.send_text.assert_called_once()
    mock_ws3.send_text.assert_called_once()


@pytest.mark.asyncio
async def test_websocket_removes_disconnected_clients():
    """VERIFY: Disconnected clients are removed from active connections"""
    from app.services.websocket_manager import ConnectionManager

    manager = ConnectionManager()

    mock_ws1 = AsyncMock()
    mock_ws2 = AsyncMock()

    await manager.connect(mock_ws1)
    await manager.connect(mock_ws2)

    assert len(manager.active_connections) == 2

    # Disconnect one client
    manager.disconnect(mock_ws1)

    assert len(manager.active_connections) == 1
    assert mock_ws2 in manager.active_connections
    assert mock_ws1 not in manager.active_connections


@pytest.mark.asyncio
async def test_websocket_handles_send_failures():
    """VERIFY: WebSocket handles client send failures gracefully"""
    from app.services.websocket_manager import ConnectionManager

    manager = ConnectionManager()

    # Mock client that fails on send
    mock_ws_fail = AsyncMock()
    mock_ws_fail.send_text = AsyncMock(side_effect=Exception("Connection lost"))

    mock_ws_ok = AsyncMock()

    await manager.connect(mock_ws_fail)
    await manager.connect(mock_ws_ok)

    # Broadcast should handle failure gracefully
    await manager.broadcast({"test": "message"})

    # Failed client should be removed
    assert mock_ws_fail not in manager.active_connections
    # Working client should still be connected
    assert mock_ws_ok in manager.active_connections


# ============================================================================
# Log Enrichment Tests
# ============================================================================

@pytest.mark.asyncio
async def test_user_extracted_from_jwt():
    """VERIFY: User ID/name extracted from request state"""
    from app.middleware.logging_middleware import LoggingMiddleware

    received_logs = []
    with patch("app.services.websocket_manager.websocket_logger.log", new_callable=AsyncMock) as mock_log:
        mock_log.side_effect = lambda **kwargs: received_logs.append(kwargs)

        async def mock_call_next(req): return JSONResponse({"status": "ok"})

        scope = {
            "type": "http",
            "method": "GET",
            "path": "/api/v1/assets",
            "headers": [],
            "query_string": b"",
        }

        request = Request(scope, AsyncMock(), AsyncMock())

        # Mock user in request state
        mock_user = Mock()
        mock_user.id = "user-123"
        mock_user.email = "user@example.com"
        request.state.user = mock_user

        middleware = LoggingMiddleware(Mock())
        await middleware.dispatch(request, mock_call_next)

        # Verify user info in log
        assert received_logs[0]["user_id"] == "user-123"
        assert received_logs[0]["user_name"] == "user@example.com"


# ============================================================================
# Real-Time Streaming Test
# ============================================================================

@pytest.mark.asyncio
async def test_logs_stream_in_real_time():
    """VERIFY: Logs appear immediately, not batched"""
    from app.services.websocket_manager import ConnectionManager

    manager = ConnectionManager()
    mock_ws = AsyncMock()

    await manager.connect(mock_ws)

    # Send 3 logs rapidly
    for i in range(3):
        await manager.broadcast({"message": f"Log {i}"})

    # All 3 should have been sent immediately
    assert mock_ws.send_text.call_count == 3
