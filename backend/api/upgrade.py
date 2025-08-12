"""
This API module handles the initiation of the code transformation workflow.
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from backend.transformation.orchestration import transformation_orchestrator, TransformationOrchestrator

router = APIRouter()


class UpgradeRequest(BaseModel):
    repo_url: str = Field(..., example="https://github.com/example/project")
    prompt: str = Field(..., example="Refactor the database layer to use the Repository pattern.")

class JobResponse(BaseModel):
    job_id: str


@router.post("/upgrade/start", response_model=JobResponse, status_code=202, tags=["Upgrade"])
async def start_upgrade(
    req: UpgradeRequest,
    orchestrator: TransformationOrchestrator = Depends(lambda: transformation_orchestrator)
) -> JobResponse:
    """
    Starts the full transformation workflow for a given repository.
    """
    job_id = orchestrator.start_transformation_workflow(
        repo_url=req.repo_url,
        prompt=req.prompt
    )
    return JobResponse(job_id=job_id)


@router.get("/upgrade/status/{job_id}", tags=["Upgrade"])
async def get_upgrade_status(
    job_id: str,
    orchestrator: TransformationOrchestrator = Depends(lambda: transformation_orchestrator)
):
    """
    Retrieves the status of a transformation job.
    """
    return orchestrator.get_job_status(job_id)
