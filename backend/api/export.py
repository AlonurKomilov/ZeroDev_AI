import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from backend.core.database import get_session
from backend.core.security import current_active_user
from backend.models.user_model import User
from backend.models.project_model import Project
from backend.tasks.project_tasks import export_project_zip_task
from pydantic import BaseModel

router = APIRouter()

class ExportResponse(BaseModel):
    task_id: str

@router.post("/projects/{project_id}/export", response_model=ExportResponse, status_code=202)
def export_project(
    *,
    session: Session = Depends(get_session),
    current_user: User = Depends(current_active_user),
    project_id: uuid.UUID,
):
    """
    Trigger a background task to export a project to a zip file.
    """
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this project")

    task = export_project_zip_task.delay(str(current_user.id), str(project.id))

    return ExportResponse(task_id=task.id)
