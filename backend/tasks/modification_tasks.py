import asyncio

from backend.agents.code_patcher_agent import code_patcher_agent
from backend.agents.context_builder_agent import context_builder_agent
from backend.agents.review_agent import review_agent
from backend.core.celery_app import celery_app
from backend.core.orchestration_service import ModificationState, orchestration_service
from backend.services.prompt_enrichment_service import prompt_enrichment_service


@celery_app.task
def build_context_task(job_id: str):
    """
    Celery task to build the context for a modification job.
    """
    # ... (code from previous turn, unchanged)
    print(f"Executing build_context_task for job_id: {job_id}")
    job = orchestration_service.get_job_status(job_id)

    if not job or job.get("error"):
        print(f"Error: Could not retrieve job details for job_id: {job_id}")
        return

    try:
        project_id = job["project_id"]
        prompt = job["prompt"]
        user_id = job["user_id"]
    except KeyError as e:
        error_message = f"Missing essential data in job details: {e}"
        print(f"Error for job_id {job_id}: {error_message}")
        orchestration_service.update_job_state(
            job_id, ModificationState.ERROR, {"error_message": error_message}
        )
        return

    context = context_builder_agent.build_context(user_id, project_id, prompt)

    if "error" in context:
        orchestration_service.update_job_state(
            job_id, ModificationState.ERROR, {"error_message": context["error"]}
        )
        return

    orchestration_service.update_job_state(
        job_id, ModificationState.CODE_PATCHING, {"context": context}
    )

    generate_patch_task.delay(job_id)
    print(
        f"Successfully built context for job_id: {job_id}. Transitioning to CODE_PATCHING."
    )


@celery_app.task
def generate_patch_task(job_id: str):
    """
    Celery task to generate the diff patch for a modification job.
    """
    # ... (code from previous turn, unchanged)
    print(f"Executing generate_patch_task for job_id: {job_id}")
    job = orchestration_service.get_job_status(job_id)

    if not job or job.get("error"):
        print(f"Error: Could not retrieve job details for job_id: {job_id}")
        return

    try:
        prompt = job["prompt"]
        context = job["context"]
    except KeyError as e:
        error_message = f"Missing essential data in job details: {e}"
        print(f"Error for job_id {job_id}: {error_message}")
        orchestration_service.update_job_state(
            job_id, ModificationState.ERROR, {"error_message": error_message}
        )
        return

    enriched_prompt = prompt_enrichment_service.enrich_prompt(prompt)

    patch = asyncio.run(code_patcher_agent.generate_patch(enriched_prompt, context))

    if patch.startswith("Error:"):
        orchestration_service.update_job_state(
            job_id, ModificationState.ERROR, {"error_message": patch}
        )
        return

    orchestration_service.update_job_state(
        job_id, ModificationState.REVIEWING, {"diff_patch": patch}
    )

    review_patch_task.delay(job_id)
    print(
        f"Successfully generated patch for job_id: {job_id}. Transitioning to REVIEWING."
    )


@celery_app.task
def review_patch_task(job_id: str):
    """
    Celery task to review the generated patch.
    """
    print(f"Executing review_patch_task for job_id: {job_id}")
    job = orchestration_service.get_job_status(job_id)

    if not job or job.get("error"):
        print(f"Error: Could not retrieve job details for job_id: {job_id}")
        return

    try:
        user_id = job["user_id"]
        project_id = job["project_id"]
        diff_patch = job["diff_patch"]
    except KeyError as e:
        error_message = f"Missing essential data in job details: {e}"
        print(f"Error for job_id {job_id}: {error_message}")
        orchestration_service.update_job_state(
            job_id, ModificationState.ERROR, {"error_message": error_message}
        )
        return

    review = review_agent.review_patch(user_id, project_id, diff_patch)

    if not review["success"]:
        orchestration_service.update_job_state(
            job_id,
            ModificationState.ERROR,
            {"error_message": f"Review failed: {review.get('error')}"},
        )
        return

    orchestration_service.update_job_state(
        job_id, ModificationState.AWAITING_APPROVAL, {"review_feedback": review}
    )

    print(
        f"Successfully reviewed patch for job_id: {job_id}. Transitioning to AWAITING_APPROVAL."
    )
    return {"status": "patch reviewed", "job_id": job_id}
