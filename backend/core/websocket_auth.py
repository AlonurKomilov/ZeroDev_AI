"""
WebSocket Authentication Service
Handles JWT token validation for WebSocket connections
"""

from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from typing import Optional
import logging

from models.user import User
from core.settings import Settings
from core.database import get_db
from sqlalchemy.orm import Session

settings = Settings()
logger = logging.getLogger(__name__)

async def get_current_user_ws(token: str) -> Optional[User]:
    """
    Validate JWT token for WebSocket connections
    Returns User object if valid, None otherwise
    """
    try:
        if not token:
            return None
        
        # Remove 'Bearer ' prefix if present
        if token.startswith('Bearer '):
            token = token[7:]
        
        # Decode JWT token
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        
        # Get user from database
        db = next(get_db())
        try:
            user = db.query(User).filter(User.id == user_id).first()
            return user
        finally:
            db.close()
            
    except JWTError as e:
        logger.warning(f"JWT validation error for WebSocket: {e}")
        return None
    except Exception as e:
        logger.error(f"WebSocket auth error: {e}")
        return None

async def validate_websocket_token(token: str) -> dict:
    """
    Validate WebSocket token and return user info
    Used for initial WebSocket handshake
    """
    try:
        user = await get_current_user_ws(token)
        
        if not user:
            return {
                "valid": False,
                "error": "Invalid or expired token"
            }
        
        return {
            "valid": True,
            "user": {
                "id": str(user.id),
                "email": user.email,
                "role": getattr(user, 'role', 'user'),
                "is_active": getattr(user, 'is_active', True)
            }
        }
        
    except Exception as e:
        logger.error(f"WebSocket token validation error: {e}")
        return {
            "valid": False,
            "error": "Token validation failed"
        }
