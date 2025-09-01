import uuid

from backend.core.database import get_session
from backend.core.settings import settings
from backend.models.user_model import User
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users_db_sqlmodel import SQLModelUserDatabase


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    """
    Manages user-related operations.
    """

    reset_password_token_secret = settings.JWT_SECRET
    verification_token_secret = settings.JWT_SECRET

    async def on_after_register(self, user: User, request=None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(self, user: User, token: str, request=None):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(self, user: User, token: str, request=None):
        print(f"Verification requested for user {user.id}. Verification token: {token}")


def get_user_db(session=Depends(get_session)):
    yield SQLModelUserDatabase(session, User)


def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.JWT_SECRET, lifetime_seconds=3600)


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

current_active_user = fastapi_users.current_user(active=True)

# Define the API key header for the emergency key
emergency_api_key_header = APIKeyHeader(name="X-Emergency-Key", auto_error=False)


async def get_owner_emergency_key(api_key: str = Depends(emergency_api_key_header)):
    """
    Dependency to verify the owner's emergency key.
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Emergency key is missing.",
        )
    if api_key != settings.OWNER_EMERGENCY_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid emergency key.",
        )
    return api_key


async def get_current_user_ws(token: str) -> Optional[User]:
    """
    Real authentication for WebSocket connections using JWT tokens
    """
    try:
        from jose import JWTError, jwt
        from backend.core.database import get_session
        from sqlmodel import select
        
        # Decode the JWT token
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET, 
            algorithms=["HS256"]
        )
        user_id = payload.get("sub")
        
        if user_id is None:
            return None
            
        # Get user from database
        session = next(get_session())
        statement = select(User).where(User.id == user_id)
        user = session.exec(statement).first()
        
        return user
        
    except (JWTError, Exception) as e:
        # Log the error but don't expose details
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"WebSocket authentication failed: {str(e)}")
        return None
