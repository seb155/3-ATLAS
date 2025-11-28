"""
Logging middleware that captures all HTTP requests and broadcasts them via WebSocket.
"""

import time
import uuid
from collections.abc import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.services.websocket_manager import WebSocketLogger


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests and broadcast to WebSocket clients."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip WebSocket upgrades and health checks for noise reduction
        if request.url.path in ["/health", "/ws/logs", "/docs", "/openapi.json", "/redoc"]:
            return await call_next(request)

        # Skip OPTIONS requests
        if request.method == "OPTIONS":
            return await call_next(request)

        request_id = str(uuid.uuid4())[:8]
        start_time = time.time()

        # Extract request info
        method = request.method
        path = request.url.path
        client_ip = request.client.host if request.client else "unknown"

        # Extract user context from request (if JWT is present)
        user_id = None
        user_name = None
        try:
            # Try to get user from request state (set by auth dependencies)
            user = getattr(request.state, "user", None)
            if user:
                user_id = str(user.id) if hasattr(user, "id") else None
                user_name = user.email if hasattr(user, "email") else None
        except Exception:
            pass  # No user context available

        # Auto-detect topic from path
        topic = self._detect_topic(path)

        # Log request start (DEBUG level for User mode filtering)
        await self._broadcast_log(
            level="DEBUG",
            message=f"{method} {path}",
            source="BACKEND",
            action_type="REQUEST",
            user_id=user_id,
            user_name=user_name,
            topic=topic,
            context={
                "request_id": request_id,
                "client_ip": client_ip,
                "method": method,
                "path": path,
            },
        )

        # Process request
        try:
            response = await call_next(request)
            duration_ms = (time.time() - start_time) * 1000

            # Determine log level based on status code
            status_code = response.status_code
            if status_code >= 500:
                level = "ERROR"
            elif status_code >= 400:
                level = "WARN"
            else:
                level = "INFO"

            # Log response with performance metrics
            await self._broadcast_log(
                level=level,
                message=f"{method} {path} → {status_code} ({duration_ms:.0f}ms)",
                source="BACKEND",
                action_type="RESPONSE",
                user_id=user_id,
                user_name=user_name,
                topic=topic,
                response_time=round(duration_ms, 2),
                context={
                    "request_id": request_id,
                    "status_code": status_code,
                    "duration_ms": round(duration_ms, 2),
                    "method": method,
                    "path": path,
                },
            )

            return response

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000

            # Log error
            await self._broadcast_log(
                level="ERROR",
                message=f"{method} {path} → ERROR: {str(e)}",
                source="BACKEND",
                action_type="ERROR",
                user_id=user_id,
                user_name=user_name,
                topic=topic,
                context={
                    "request_id": request_id,
                    "error": str(e),
                    "duration_ms": round(duration_ms, 2),
                },
            )
            raise

    def _detect_topic(self, path: str) -> str:
        """Auto-detect log topic from API path."""
        path_lower = path.lower()

        if "/assets" in path_lower:
            return "ASSETS"
        elif "/rules" in path_lower:
            return "RULES"
        elif "/cables" in path_lower:
            return "CABLES"
        elif "/import" in path_lower or "/upload" in path_lower:
            return "IMPORT"
        elif "/auth" in path_lower or "/login" in path_lower or "/token" in path_lower:
            return "AUTH"
        elif "/projects" in path_lower or "/project" in path_lower:
            return "PROJECT"
        elif "/io" in path_lower or "/io-list" in path_lower:
            return "IO_LISTS"

        return "SYSTEM"

    async def _broadcast_log(
        self,
        level: str,
        message: str,
        source: str = "BACKEND",
        action_type: str | None = None,
        user_id: str | None = None,
        user_name: str | None = None,
        topic: str | None = None,
        response_time: float | None = None,
        context: dict | None = None,
    ):
        """Broadcast log entry to all WebSocket clients via WebSocketLogger."""
        await WebSocketLogger.log(
            level=level,
            message=message,
            source=source,
            action_type=action_type,
            user_id=user_id,
            user_name=user_name,
            topic=topic,
            response_time=response_time,
            context=context,
        )
