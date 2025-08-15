import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import Session

# We'll need access to the session to verify project ownership
from backend.core.database import get_session
from backend.core.orchestration_service import orchestration_service
from backend.core.security import current_active_user
from backend.models.project_model import Project
from backend.models.user_model import User

router = APIRouter()


class ModifyRequest(BaseModel):
    project_id: uuid.UUID = Field(..., description="The ID of the project to modify.")
    prompt: str = Field(
        ..., description="The natural language prompt describing the modification."
    )


class ModifyResponse(BaseModel):
    job_id: str = Field(..., description="The ID of the asynchronous modification job.")


@router.post("/", response_model=ModifyResponse, status_code=202)
def start_modification_job(
    *,
    session: Session = Depends(get_session),
    current_user: User = Depends(current_active_user),
    modify_request: ModifyRequest,
):
    """
    Receives a user's request to modify a project and dispatches a job
    to the Central Orchestration Service.
    """
    # Verify that the project exists and the user has access to it.
    project = session.get(Project, modify_request.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to access this project"
        )

    # Dispatch the job to the orchestration service.
    try:
        job_id = orchestration_service.start_modification_workflow(
            user_id=str(current_user.id),
            project_id=str(modify_request.project_id),
            prompt=modify_request.prompt,
        )
        return ModifyResponse(job_id=job_id)
    except Exception as e:
        # This could catch issues with starting the workflow itself.
        raise HTTPException(
            status_code=500, detail=f"Failed to start modification job: {e}"
        )
