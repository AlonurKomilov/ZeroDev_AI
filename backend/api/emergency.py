"""
Emergency Override API

This API provides a highly secure endpoint for performing emergency actions,
such as activating a system-wide safe mode or initiating a shutdown.
Access to this API is restricted to the owner via a special emergency key.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from redis import Redis

from backend.core.redis import get_redis
from backend.core.security import get_owner_emergency_key

router = APIRouter()


class EmergencyAction(BaseModel):
    action: str  # e.g., "SAFE_MODE", "SHUTDOWN"


@router.post("/override", include_in_schema=False)
async def emergency_override(
    action: EmergencyAction,
    emergency_key: str = Depends(get_owner_emergency_key),
    redis: Redis = Depends(get_redis),
):
    """
    A hidden endpoint for emergency actions.
    Authenticates using the owner's emergency key.
    """
    if action.action == "SAFE_MODE":
        redis.set("system:status", "SAFE_MODE")
        return {"message": "System is now in SAFE_MODE."}
    elif action.action == "SHUTDOWN":
        redis.set("system:status", "SHUTDOWN")
        return {"message": "System is now in SHUTDOWN mode."}
    elif action.action == "NORMAL":
        redis.delete("system:status")
        return {"message": "System is now in NORMAL mode."}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid action.",
        )
