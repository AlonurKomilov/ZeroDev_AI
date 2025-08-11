"""
Migration API

This API provides endpoints for users to export their data from the platform.
"""
from fastapi import APIRouter, Depends, status
from backend.core.security import current_active_user
from backend.models.user_model import User
from backend.tasks.migration_tasks import export_user_data_task
from pydantic import BaseModel

router = APIRouter()

class MigrationResponse(BaseModel):
    task_id: str

@router.post("/export", response_model=MigrationResponse, status_code=status.HTTP_202_ACCEPTED)
async def export_user_data(
    user: User = Depends(current_active_user),
):
    """
    Triggers a background task to export all of a user's data.
    """
    task = export_user_data_task.delay(user_id=str(user.id))
    return MigrationResponse(task_id=task.id)
