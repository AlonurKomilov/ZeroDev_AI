"""
Global Status Middleware

This middleware checks for a global system status on every request and can
take actions like blocking requests based on the current status.
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from backend.core.redis import get_redis
from backend.core.security import get_jwt_strategy, get_user_manager, bearer_transport
from backend.models.user_model import User
import logging

log = logging.getLogger(__name__)

class GlobalStatusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        redis = get_redis()
        if not redis:
            response = await call_next(request)
            return response

        system_status = redis.get("system:status")

        if system_status == "SHUTDOWN":
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={"detail": "The system is currently down for maintenance."},
            )

        if system_status == "SAFE_MODE":
            is_superuser = False
            try:
                token = await bearer_transport.scheme(request)
                if token:
                    strategy = get_jwt_strategy()
                    async for user_manager in get_user_manager():
                        user = await strategy.read_token(token, user_manager)
                        if user and user.is_active:
                            is_superuser = user.is_superuser
            except Exception as e:
                log.warning(f"Error while checking for superuser in middleware: {e}")
                pass  # Treat as not a superuser

            if not is_superuser:
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"detail": "The system is in safe mode. Only admins can access it."},
                )

        response = await call_next(request)
        return response
