from fastapi import APIRouter, Depends, HTTPException
from fastapi import Path as FastApiPath
from pydantic import BaseModel, Field

from backend.core.orchestration_service import ModificationState, orchestration_service
from backend.core.security import current_active_user
from backend.models.user_model import User
from backend.services.apply_patch_service import apply_patch_service

router = APIRouter()


class DiffResponse(BaseModel):
    job_id: str = Field(..., description="The ID of the modification job.")
    status: str = Field(..., description="The current status of the job.")
    diff_patch: str = Field(..., description="The generated diff patch for review.")


class ApplyResponse(BaseModel):
    job_id: str = Field(..., description="The ID of the modification job.")
    status: str = Field(
        ..., description="The final status after attempting to apply the patch."
    )
    message: str = Field(..., description="A message indicating the result.")


@router.get("/{job_id}", response_model=DiffResponse)
def get_diff_for_review(
    *,
    job_id: str = FastApiPath(
        ..., description="The ID of the modification job to review."
    ),
    current_user: User = Depends(current_active_user),
):
    """
    Allows the frontend to fetch the generated diff file for user review.
    """
    job = orchestration_service.get_job_status(job_id)
    if not job or "error" in job:
        raise HTTPException(
            status_code=404, detail=f"Job with ID '{job_id}' not found."
        )

    # Authorization check: Ensure the user requesting the review owns the job.
    if job.get("user_id") != str(current_user.id):
        raise HTTPException(
            status_code=403, detail="You are not authorized to review this job."
        )

    if job["state"] != ModificationState.AWAITING_APPROVAL:
        raise HTTPException(
            status_code=400,
            detail=f"Job is in state '{job['state']}', not awaiting approval. Cannot fetch diff.",
        )

    return DiffResponse(
        job_id=job_id,
        status=job["state"],
        diff_patch=job.get("diff_patch", "# No diff generated or available."),
    )


@router.post("/{job_id}/apply", response_model=ApplyResponse)
def apply_reviewed_patch(
    *,
    job_id: str = FastApiPath(
        ..., description="The ID of the modification job to apply."
    ),
    current_user: User = Depends(current_active_user),
):
    """
    Upon user approval, triggers the service to safely apply the patch to the project files.
    """
    job = orchestration_service.get_job_status(job_id)
    if not job or "error" in job:
        raise HTTPException(
            status_code=404, detail=f"Job with ID '{job_id}' not found."
        )

    if job.get("user_id") != str(current_user.id):
        raise HTTPException(
            status_code=403, detail="You are not authorized to apply this patch."
        )

    if job["state"] != ModificationState.AWAITING_APPROVAL:
        raise HTTPException(
            status_code=400,
            detail=f"Patch cannot be applied. Job is in state '{job['state']}', not awaiting approval.",
        )

    # Update state to show work is in progress
    orchestration_service.update_job_state(job_id, ModificationState.APPLYING_PATCH)

    result = apply_patch_service.apply_patch(
        user_id=job["user_id"],
        project_id=job["project_id"],
        diff_patch=job["diff_patch"],
    )

    if result["success"]:
        orchestration_service.update_job_state(job_id, ModificationState.DONE)
        return ApplyResponse(
            job_id=job_id, status="success", message="Patch applied successfully."
        )
    else:
        error_detail = result.get("error", "An unknown error occurred.")
        orchestration_service.update_job_state(
            job_id,
            ModificationState.ERROR,
            {"error_message": f"Failed during patch application: {error_detail}"},
        )
        # We return a 500 error because the application process failed on the backend.
        raise HTTPException(status_code=500, detail=error_detail)
