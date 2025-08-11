from fastapi import APIRouter
from backend.core.security import auth_backend, fastapi_users
from backend.schemas.user_schemas import UserCreate, UserRead, UserUpdate

router = APIRouter()

# Include the main auth router from fastapi-users
# /login, /logout
router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/jwt",
    tags=["auth"],
)

# Include the register router from fastapi-users
# /register
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="",
    tags=["auth"],
)

# Include the reset password router from fastapi-users
# /forgot-password, /reset-password
router.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="",
    tags=["auth"],
)

# Include the verify router from fastapi-users
# /request-verify-token, /verify
router.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="",
    tags=["auth"],
)

# Include the users router from fastapi-users
# /users/me, /users/{id}
router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)
