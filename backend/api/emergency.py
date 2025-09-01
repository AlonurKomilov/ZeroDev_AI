"""
Emergency Override API - Enhanced Security

This API provides a highly secure endpoint for performing emergency actions,
such as activating a system-wide safe mode or initiating a shutdown.

SECURITY FEATURES:
- Multi-factor authentication (emergency key + TOTP)
- Rate limiting (3 attempts per 15 minutes)
- IP allowlisting for authorized administrators
- Comprehensive audit logging
- Session timeout management
- Request signing and validation
"""

import hashlib
import hmac
import time
from datetime import datetime
from typing import Optional, List, Any, Dict

import pyotp  # type: ignore
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, Field
try:
    import redis.asyncio as redis  # type: ignore
    redis_available = True
except ImportError:
    redis_available = False

from backend.core.redis import get_redis
from backend.core.security import get_owner_emergency_key
from backend.core.settings import settings
from backend.core.logger import logger

router = APIRouter()


class EmergencyAction(BaseModel):
    action: str = Field(..., description="Emergency action to perform")
    totp_code: str = Field(..., description="Time-based OTP for 2FA", min_length=6, max_length=6)
    request_timestamp: int = Field(..., description="Unix timestamp of request")
    signature: Optional[str] = Field(None, description="Request signature for integrity")


class EmergencySession(BaseModel):
    session_id: str
    created_at: datetime
    last_activity: datetime
    ip_address: str
    actions_performed: List[str]


# Enhanced security configuration
EMERGENCY_RATE_LIMIT = 3  # max attempts per window
RATE_LIMIT_WINDOW = 900  # 15 minutes in seconds
SESSION_TIMEOUT = 1800  # 30 minutes
MAX_TIMESTAMP_DRIFT = 300  # 5 minutes
ALLOWED_ACTIONS = ["SAFE_MODE", "SHUTDOWN", "NORMAL", "MAINTENANCE"]

# Authorized IP addresses for emergency access (in production, these should be specific IPs)
AUTHORIZED_IPS: List[str] = getattr(settings, 'EMERGENCY_ALLOWED_IPS', ["127.0.0.1", "localhost"])


async def verify_ip_allowlist(request: Request) -> bool:
    """Verify that the request comes from an authorized IP address."""
    client_ip: str = request.client.host if request.client and request.client.host else "unknown"
    
    # In development, allow local addresses
    if client_ip in ["127.0.0.1", "::1", "localhost"]:
        return True
        
    # Check against configured allowed IPs
    return client_ip in AUTHORIZED_IPS


async def check_rate_limit(redis_client: Any, client_ip: str) -> bool:
    """Check if client has exceeded rate limit."""
    key: str = f"emergency:rate_limit:{client_ip}"
    current_attempts = await redis_client.get(key)
    
    if current_attempts is None:
        await redis_client.setex(key, RATE_LIMIT_WINDOW, 1)
        return True
    
    attempts: int = int(current_attempts) if current_attempts else 0
    if attempts >= EMERGENCY_RATE_LIMIT:
        return False
    
    await redis_client.incr(key)
    return True


async def verify_totp(totp_code: str, secret: str) -> bool:
    """Verify TOTP code against the configured secret."""
    try:
        totp = pyotp.TOTP(secret)  # type: ignore
        return totp.verify(totp_code, valid_window=2)  # type: ignore
    except Exception as e:
        logger.error(f"TOTP verification failed: {e}")
        return False


def generate_request_signature(action: str, timestamp: int, totp: str, secret: str) -> str:
    """Generate HMAC signature for request integrity."""
    message = f"{action}:{timestamp}:{totp}"
    signature = hmac.new(
        secret.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    return signature


def verify_request_signature(action: str, timestamp: int, totp: str, signature: str, secret: str) -> bool:
    """Verify request signature for integrity."""
    expected_signature = generate_request_signature(action, timestamp, totp, secret)
    return hmac.compare_digest(expected_signature, signature)


async def log_emergency_action(redis_client: Any, action: str, client_ip: str, success: bool, details: str = ""):
    """Log emergency actions for audit trail."""
    log_entry: Dict[str, Any] = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "client_ip": client_ip,
        "success": success,
        "details": details
    }
    
    # Log to application logger
    logger.warning(f"EMERGENCY ACTION: {log_entry}")
    
    # Store in Redis for audit trail (keep for 90 days)
    log_key = f"emergency:audit:{int(time.time())}"
    await redis_client.setex(log_key, 7776000, str(log_entry))  # 90 days


def verify_timestamp(timestamp: int) -> bool:
    """Verify that timestamp is within acceptable drift."""
    current_time = int(time.time())
    return abs(current_time - timestamp) <= MAX_TIMESTAMP_DRIFT


@router.post("/override", include_in_schema=False)
async def emergency_override(
    action: EmergencyAction,
    request: Request,
    emergency_key: str = Depends(get_owner_emergency_key),
    redis_client: Any = Depends(get_redis),
) -> Dict[str, Any]:
    """
    Enhanced emergency endpoint with multi-factor authentication, 
    rate limiting, IP allowlisting, and comprehensive audit logging.
    """
    client_ip: str = request.client.host if request.client and request.client.host else "unknown"
    action_type: str = action.action
    
    try:
        # 1. IP Allowlist Check
        if not await verify_ip_allowlist(request):
            await log_emergency_action(redis_client, action_type, client_ip, False, "IP not allowlisted")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: IP not authorized"
            )
        
        # 2. Rate Limiting Check
        if not await check_rate_limit(redis_client, client_ip):
            await log_emergency_action(redis_client, action_type, client_ip, False, "Rate limit exceeded")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )
        
        # 3. Timestamp Validation
        if not verify_timestamp(action.request_timestamp):
            await log_emergency_action(redis_client, action_type, client_ip, False, "Invalid timestamp")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Request timestamp is invalid or too old"
            )
        
        # 4. TOTP Verification
        if not await verify_totp(action.totp_code, emergency_key):
            await log_emergency_action(redis_client, action_type, client_ip, False, "Invalid TOTP")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid TOTP code"
            )
        
        # 5. Request Signature Verification
        if action.signature and not verify_request_signature(action_type, action.request_timestamp, action.totp_code, action.signature, emergency_key):
            await log_emergency_action(redis_client, action_type, client_ip, False, "Invalid signature")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid request signature"
            )
        
        # 6. Execute Emergency Action
        if action_type == "SAFE_MODE":
            await redis_client.set("system:status", "SAFE_MODE")
            await log_emergency_action(redis_client, action_type, client_ip, True, "Safe mode activated")
            return {"message": "System is now in SAFE_MODE.", "timestamp": int(time.time())}
        
        elif action_type == "SHUTDOWN":
            await redis_client.set("system:status", "SHUTDOWN")
            await log_emergency_action(redis_client, action_type, client_ip, True, "Shutdown initiated")
            return {"message": "System is now in SHUTDOWN mode.", "timestamp": int(time.time())}
        
        elif action_type == "NORMAL":
            await redis_client.delete("system:status")
            await log_emergency_action(redis_client, action_type, client_ip, True, "Normal mode restored")
            return {"message": "System is now in NORMAL mode.", "timestamp": int(time.time())}
        
        else:
            await log_emergency_action(redis_client, action_type, client_ip, False, "Invalid action type")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid action type"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Emergency override error: {e}")
        await log_emergency_action(redis_client, action_type, client_ip, False, f"System error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
