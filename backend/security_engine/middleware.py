"""
Security Middleware for FastAPI Integration

This middleware integrates the Security Engine with FastAPI requests,
providing automatic security checks, rate limiting, and logging.
"""

import time
from typing import Callable, List, Optional

from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from backend.security_engine import security_engine, SecurityViolation
from backend.core.logger import get_logger

logger = get_logger(__name__)


class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Security middleware that integrates the Security Engine with FastAPI
    """
    
    def __init__(self, app, exempt_paths: Optional[List[str]] = None):
        super().__init__(app)
        self.exempt_paths = exempt_paths or [
            "/docs",
            "/redoc", 
            "/openapi.json",
            "/health",
            "/favicon.ico",
            "/static"
        ]
    
    def is_exempt_path(self, path: str) -> bool:
        """Check if path is exempt from security checks"""
        return any(path.startswith(exempt) for exempt in self.exempt_paths)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Main middleware dispatch method
        """
        start_time = time.time()
        path = request.url.path
        
        # Skip security checks for exempt paths
        if self.is_exempt_path(path):
            return await call_next(request)
        
        try:
            # Extract content for security validation (for POST/PUT requests)
            content = None
            if request.method in ["POST", "PUT", "PATCH"]:
                try:
                    # Read body for content validation
                    body = await request.body()
                    if body:
                        content = body.decode('utf-8')
                        # Re-create request with body for downstream processing
                        request._body = body
                except Exception as e:
                    logger.warning(f"Could not read request body: {e}")
            
            # Perform security check
            allowed, violations = await security_engine.perform_security_check(
                request, content, path
            )
            
            # Handle security violations
            if not allowed:
                return await self._handle_security_violation(request, violations)
            
            # Process request
            response = await call_next(request)
            
            # Add security headers
            self._add_security_headers(response)
            
            # Log successful request
            process_time = time.time() - start_time
            logger.info(f"Request processed: {request.method} {path} - {response.status_code} - {process_time:.3f}s")
            
            # Log warnings if any
            warning_violations = [v for v in violations if v.severity in ["medium", "high"]]
            if warning_violations:
                logger.warning(f"Security warnings for {path}: {len(warning_violations)} violations")
            
            return response
            
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            logger.error(f"Security middleware error: {e}")
            # Allow request to proceed but log error
            try:
                response = await call_next(request)
                self._add_security_headers(response)
                return response
            except Exception as inner_e:
                logger.error(f"Request processing failed: {inner_e}")
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content={"detail": "Internal server error"}
                )
    
    async def _handle_security_violation(self, request: Request, violations: List[SecurityViolation]) -> JSONResponse:
        """Handle security violations"""
        
        # Get the most severe violation
        severity_order = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        most_severe = max(violations, key=lambda v: severity_order.get(v.severity, 0))
        
        # Determine response based on violation type
        if most_severe.violation_type == "rate_limit":
            status_code = status.HTTP_429_TOO_MANY_REQUESTS
            message = "Rate limit exceeded. Please slow down your requests."
        elif most_severe.violation_type in ["content_policy", "content_length"]:
            status_code = status.HTTP_400_BAD_REQUEST
            message = "Request content violates security policies."
        else:
            status_code = status.HTTP_403_FORBIDDEN
            message = "Request blocked by security policies."
        
        # Prepare response
        response_data = {
            "detail": message,
            "security_violations": [
                {
                    "type": v.violation_type,
                    "severity": v.severity,
                    "message": v.message
                }
                for v in violations
            ]
        }
        
        # Add rate limit headers for rate limiting violations
        response = JSONResponse(status_code=status_code, content=response_data)
        
        if most_severe.violation_type == "rate_limit":
            response.headers["X-RateLimit-Limit"] = "60"
            response.headers["X-RateLimit-Remaining"] = "0"
            response.headers["X-RateLimit-Reset"] = str(int(time.time()) + 60)
        
        self._add_security_headers(response)
        
        return response
    
    def _add_security_headers(self, response: Response):
        """Add security headers to response"""
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY", 
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
            "X-Security-Engine": "ZeroDev-AI-v1.0"
        }
        
        for header, value in security_headers.items():
            response.headers[header] = value


# Security decorator for specific endpoints
def require_security_check(content_validation: bool = True):
    """
    Decorator to enforce security checks on specific endpoints
    """
    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            # This would be used for endpoints that need extra security
            # For now, the middleware handles all security
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator
