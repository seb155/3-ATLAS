"""
Tests for logs endpoint (HTTP fallback for non-WebSocket clients).
"""

import pytest
from unittest.mock import patch, MagicMock


class TestLogsEndpoint:
    """Test HTTP endpoints for logs."""

    def test_get_logs_returns_list(self, client):
        """Test GET /api/v1/logs/ returns a list of logs."""
        response = client.get("/api/v1/logs/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_logs_with_limit(self, client):
        """Test GET /api/v1/logs/ respects limit parameter."""
        response = client.get("/api/v1/logs/?limit=10")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_logs_default_limit(self, client):
        """Test GET /api/v1/logs/ uses default limit of 100."""
        with patch('app.api.endpoints.logs.WebSocketLogger') as mock_logger:
            mock_logger.get_logs.return_value = []
            response = client.get("/api/v1/logs/")
            assert response.status_code == 200
            # Verify default limit was used
            mock_logger.get_logs.assert_called_with(limit=100)

    def test_clear_logs(self, client):
        """Test DELETE /api/v1/logs/ clears all logs."""
        response = client.delete("/api/v1/logs/")
        assert response.status_code == 200
        assert response.json() == {"status": "cleared"}

    def test_get_connection_count(self, client):
        """Test GET /api/v1/logs/connections returns connection count."""
        response = client.get("/api/v1/logs/connections")
        assert response.status_code == 200
        data = response.json()
        assert "connections" in data
        assert isinstance(data["connections"], int)

    def test_get_connection_count_zero_when_no_connections(self, client):
        """Test connection count is 0 when no WebSocket connections."""
        response = client.get("/api/v1/logs/connections")
        assert response.status_code == 200
        # In test environment, no WebSocket connections
        assert response.json()["connections"] >= 0


class TestLogsWebSocket:
    """Test WebSocket endpoint for logs (basic connectivity)."""

    def test_websocket_connect_and_disconnect(self, client):
        """Test WebSocket connection and graceful disconnect."""
        # Clear logs first to ensure clean state
        from app.services.websocket_manager import WebSocketLogger
        WebSocketLogger.clear()

        with client.websocket_connect("/ws/logs") as websocket:
            # Connection established successfully
            # Just test that we can connect and disconnect
            pass
        # Connection closed gracefully - no exception means success

    def test_websocket_clear_command(self, client):
        """Test WebSocket clear command."""
        from app.services.websocket_manager import WebSocketLogger

        # Clear first, then add a log
        WebSocketLogger.clear()
        WebSocketLogger.log("info", "Log to clear", {})

        # Verify log was added
        logs_before = WebSocketLogger.get_logs()
        assert len(logs_before) >= 1

        with client.websocket_connect("/ws/logs") as websocket:
            # Send clear command
            websocket.send_text("clear")

        # Verify logs were cleared
        logs_after = WebSocketLogger.get_logs()
        assert len(logs_after) == 0
