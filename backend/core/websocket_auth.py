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
    Authenticate WebSocket connections using JWT tokens
    """
    try:
        # Decode JWT token
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET, 
            algorithms=["HS256"]
        )
        
        user_id = payload.get("sub")
        if not user_id:
            logger.warning("No user ID found in JWT token")
            return None
        
        # Get database session and fetch user
        with next(get_db()) as session:
            user = session.query(User).filter(User.id == user_id).first()
            
        if not user or not user.is_active:
            logger.warning(f"User not found or inactive: {user_id}")
            return None
            
        return user
        
    except JWTError as e:
        logger.error(f"JWT validation failed: {e}")
        return None
    except Exception as e:
        logger.error(f"WebSocket authentication error: {e}")
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
