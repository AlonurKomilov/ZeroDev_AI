import uuid
from enum import Enum


class ModificationState(str, Enum):
    """
    Defines the states of the modification workflow state machine.
    """

    IDLE = "IDLE"
    CONTEXT_BUILDING = "CONTEXT_BUILDING"
    CODE_PATCHING = "CODE_PATCHING"
    REVIEWING = "REVIEWING"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    APPLYING_PATCH = "APPLYING_PATCH"
    DONE = "DONE"
    ERROR = "ERROR"


class OrchestrationService:
    """
    The Central Orchestration Service acts as a state machine for complex, multi-step
    workflows, starting with the "modify" flow. It dispatches jobs to the Celery
    task queue and tracks their progress.
    """

    def __init__(self):
        # In a production environment, this state should be persisted in a
        # database or a distributed cache like Redis.
        self.modification_jobs = {}

    def start_modification_workflow(
        self, user_id: str, project_id: str, prompt: str
    ) -> str:
        """
        Initializes and starts the modification workflow for a given project.
        """
        job_id = str(uuid.uuid4())

        self.modification_jobs[job_id] = {
            "job_id": job_id,
            "user_id": user_id,
            "project_id": project_id,
            "prompt": prompt,
            "state": ModificationState.CONTEXT_BUILDING,
            "context": None,
            "diff_patch": None,
            "review_feedback": None,
            "error_message": None,
        }

        # Dispatch the first task in the workflow to Celery.
        from backend.tasks.modification_tasks import build_context_task

        build_context_task.delay(job_id)

        print(f"Started modification job: {job_id} for project: {project_id}")
        return job_id

    def get_job_status(self, job_id: str) -> dict:
        """
        Retrieves the current status and data of a modification job.
        """
        return self.modification_jobs.get(job_id, {"error": "Job not found"})

    def update_job_state(
        self, job_id: str, new_state: ModificationState, data: dict = None
    ):
        """
        Updates the state and associated data of a modification job.
        This method would be called by Celery tasks as they complete their work.
        """
        if job_id in self.modification_jobs:
            self.modification_jobs[job_id]["state"] = new_state
            if data:
                self.modification_jobs[job_id].update(data)
            print(f"Updated job {job_id} to state {new_state}")
        else:
            print(f"Error: Could not find job {job_id} to update.")
            # In a real system, this should raise an exception or handle the error more gracefully.


# Instantiate a singleton of the service for the application to use.
orchestration_service = OrchestrationService()
