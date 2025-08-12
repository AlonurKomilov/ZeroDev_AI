"""
This module contains the TransformationOrchestrator, which manages the
state of the end-to-end code transformation workflow.
"""
from enum import Enum
import uuid

class TransformationState(str, Enum):
    """
    Defines the states of the transformation workflow state machine.
    """
    CLONING = "CLONING"
    SCANNING = "SCANNING"
    REFACTORING = "REFACTORING"
    VALIDATING = "VALIDATING"
    CREATING_PR = "CREATING_PR"
    DONE = "DONE"
    ERROR = "ERROR"


class TransformationOrchestrator:
    """
    Acts as a state machine for the complex, multi-step transformation workflow.
    It dispatches jobs to the Celery task queue and tracks their progress.
    """
    def __init__(self):
        # In a production environment, this state should be persisted in a
        # database or a distributed cache like Redis.
        self.transformation_jobs = {}

    def start_transformation_workflow(self, repo_url: str, prompt: str) -> str:
        """
        Initializes and starts the transformation workflow for a given repository.
        """
        job_id = str(uuid.uuid4())

        self.transformation_jobs[job_id] = {
            "job_id": job_id,
            "repo_url": repo_url,
            "prompt": prompt,
            "state": TransformationState.CLONING,
            "cloned_repo_path": None,
            "architecture_map": None,
            "pull_request_url": None,
            "error_message": None,
        }

        # Dispatch the first task in the workflow to Celery.
        from backend.transformation.tasks import clone_and_scan_task
        clone_and_scan_task.delay(job_id)

        print(f"Started transformation job: {job_id} for repo: {repo_url}")
        return job_id

    def get_job_status(self, job_id: str) -> dict:
        """
        Retrieves the current status and data of a transformation job.
        """
        return self.transformation_jobs.get(job_id, {"error": "Job not found"})

    def update_job_state(self, job_id: str, new_state: TransformationState, data: dict = None):
        """
        Updates the state and associated data of a transformation job.
        This method will be called by Celery tasks as they complete their work.
        """
        if job_id in self.transformation_jobs:
            self.transformation_jobs[job_id]["state"] = new_state
            if data:
                self.transformation_jobs[job_id].update(data)
            print(f"Updated job {job_id} to state {new_state}")
        else:
            print(f"Error: Could not find job {job_id} to update.")

# Instantiate a singleton of the service for the application to use.
transformation_orchestrator = TransformationOrchestrator()
