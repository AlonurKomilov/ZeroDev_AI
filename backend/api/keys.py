from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from pydantic import BaseModel

from backend.core.database import get_session
from backend.core.security import current_active_user
from backend.models.user_model import User
from backend.services.encryption import encryption_service

router = APIRouter()

class ApiKeyCreate(BaseModel):
    service_name: str
    api_key: str

@router.post("/", status_code=201)
def add_api_key(
    *,
    session: Session = Depends(get_session),
    current_user: User = Depends(current_active_user),
    key_in: ApiKeyCreate,
):
    """
    Add or update an API key for a specific service.
    """
    encrypted_key = encryption_service.encrypt(key_in.api_key)

    if current_user.llm_api_keys is None:
        current_user.llm_api_keys = {}

    current_user.llm_api_keys[key_in.service_name] = encrypted_key

    session.add(current_user)
    session.commit()
    session.refresh(current_user)

    return {"message": f"API key for {key_in.service_name} has been added."}

@router.get("/", response_model=list[str])
def get_api_key_services(
    *,
    current_user: User = Depends(current_active_user),
):
    """
    Get the names of all services for which the user has an API key.
    """
    if current_user.llm_api_keys is None:
        return []
    return list(current_user.llm_api_keys.keys())

@router.delete("/{service_name}", status_code=204)
def delete_api_key(
    *,
    session: Session = Depends(get_session),
    current_user: User = Depends(current_active_user),
    service_name: str,
):
    """
    Delete an API key for a specific service.
    """
    if current_user.llm_api_keys and service_name in current_user.llm_api_keys:
        del current_user.llm_api_keys[service_name]
        session.add(current_user)
        session.commit()
        return {"ok": True}
    else:
        raise HTTPException(status_code=404, detail="API key for this service not found.")
