"""
This module defines the Celery tasks for the multi-step transformation
workflow, such as cloning, scanning, refactoring, and validating.
"""

import asyncio
import subprocess
import tempfile

import git

from backend.core.celery_app import celery_app
from backend.core.logger import get_logger
from backend.transformation.agents import foreign_code_scanner_agent
from backend.transformation.engine import refactoring_engine
from backend.transformation.github_service import github_service
from backend.transformation.orchestration import (
    TransformationState,
    transformation_orchestrator,
)

log = get_logger(__name__)


@celery_app.task(bind=True, name="transformation.refactor")
def refactor_task(self, job_id: str):
    """
    Celery task to perform refactoring on the codebase.
    """
    log.info(f"Starting refactor_task for job_id: {job_id}")
    try:
        # Using asyncio.run to execute the async refactor method
        asyncio.run(refactoring_engine.refactor(job_id))
    except Exception as e:
        log.error(
            f"An unexpected error occurred in refactor_task for job {job_id}: {e}"
        )
        transformation_orchestrator.update_job_state(
            job_id,
            TransformationState.ERROR,
            {"error_message": f"An unexpected error occurred during refactoring: {e}"},
        )
        raise e


@celery_app.task(bind=True, name="transformation.create_pr")
def create_pr_task(self, job_id: str):
    """
    Celery task to create a pull request with the refactored changes.
    """
    log.info(f"Starting create_pr_task for job_id: {job_id}")
    try:
        github_service.create_pull_request(job_id)
    except Exception as e:
        log.error(
            f"An unexpected error occurred in create_pr_task for job {job_id}: {e}"
        )
        # The service itself should have updated the job state to ERROR
        raise e


@celery_app.task(bind=True, name="transformation.validate")
def validation_task(self, job_id: str):
    """
    Celery task to run the test suite of the refactored code.
    """
    log.info(f"Starting validation_task for job_id: {job_id}")
    job = transformation_orchestrator.get_job_status(job_id)
    if not job or "error" in job or not job.get("cloned_repo_path"):
        log.error(f"Invalid job or missing cloned_repo_path for job_id: {job_id}")
        return

    repo_path = job["cloned_repo_path"]
    log.info(f"Running tests in {repo_path}...")

    try:
        # For now, we assume a Python project with pytest.
        # A more robust solution would detect the test framework.
        process = subprocess.run(
            ["pytest"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=300,  # 5-minute timeout for tests
        )

        if process.returncode == 0:
            log.info(f"Tests passed for job {job_id}.")
            transformation_orchestrator.update_job_state(
                job_id, TransformationState.CREATING_PR
            )
            create_pr_task.delay(job_id)
            log.info(f"Dispatched create_pr_task for job {job_id}.")
        else:
            log.error(
                f"Tests failed for job {job_id}. Return code: {process.returncode}"
            )
            error_output = f"Stdout:\n{process.stdout}\n\nStderr:\n{process.stderr}"
            transformation_orchestrator.update_job_state(
                job_id,
                TransformationState.ERROR,
                {"error_message": f"Tests failed:\n{error_output}"},
            )

    except FileNotFoundError:
        log.error(f"pytest command not found for job {job_id}.")
        transformation_orchestrator.update_job_state(
            job_id,
            TransformationState.ERROR,
            {"error_message": "Pytest not found. Cannot run validation."},
        )
    except subprocess.TimeoutExpired:
        log.error(f"Test validation timed out for job {job_id}.")
        transformation_orchestrator.update_job_state(
            job_id,
            TransformationState.ERROR,
            {"error_message": "Test validation timed out after 5 minutes."},
        )
    except Exception as e:
        log.error(
            f"An unexpected error occurred during validation for job {job_id}: {e}"
        )
        transformation_orchestrator.update_job_state(
            job_id,
            TransformationState.ERROR,
            {"error_message": f"An unexpected error occurred during validation: {e}"},
        )
        raise e


@celery_app.task(bind=True, name="transformation.clone_and_scan")
def clone_and_scan_task(self, job_id: str):
    """
    Celery task to clone a git repository and then scan it.
    """
    log.info(f"Starting clone_and_scan_task for job_id: {job_id}")
    job = transformation_orchestrator.get_job_status(job_id)
    if not job or "error" in job:
        log.error(f"Job not found for job_id: {job_id}")
        return

    repo_url = job["repo_url"]
    temp_dir = tempfile.mkdtemp()
    log.info(f"Cloning repository {repo_url} into {temp_dir}")

    try:
        # Clone the repository
        git.Repo.clone_from(repo_url, temp_dir)

        # Update the job state with the path to the cloned repo
        transformation_orchestrator.update_job_state(
            job_id, TransformationState.SCANNING, {"cloned_repo_path": temp_dir}
        )
        log.info(f"Successfully cloned repo for job {job_id}. Path: {temp_dir}")

        # Invoke the foreign code scanner agent
        foreign_code_scanner_agent(job_id)

    except git.exc.GitCommandError as e:
        log.error(f"Failed to clone repository for job {job_id}: {e}")
        transformation_orchestrator.update_job_state(
            job_id,
            TransformationState.ERROR,
            {"error_message": f"Failed to clone repository: {e}"},
        )
    except Exception as e:
        log.error(
            f"An unexpected error occurred in clone_and_scan_task for job {job_id}: {e}"
        )
        transformation_orchestrator.update_job_state(
            job_id,
            TransformationState.ERROR,
            {"error_message": f"An unexpected error occurred: {e}"},
        )
        raise e
