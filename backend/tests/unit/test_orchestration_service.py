import unittest
from unittest.mock import patch

from backend.core.orchestration_service import ModificationState, OrchestrationService


class TestOrchestrationService(unittest.TestCase):

    def setUp(self):
        self.service = OrchestrationService()

    @patch("backend.tasks.modification_tasks.build_context_task.delay")
    def test_start_modification_workflow(self, mock_delay):
        """
        Test that starting a workflow initializes the job correctly.
        """
        user_id = "test_user"
        project_id = "test_project"
        prompt = "test_prompt"

        job_id = self.service.start_modification_workflow(user_id, project_id, prompt)

        # Check that a job ID is returned
        self.assertIsNotNone(job_id)

        # Check that the Celery task was called
        mock_delay.assert_called_once_with(job_id)

        # Check the job status
        job_status = self.service.get_job_status(job_id)
        self.assertIsNotNone(job_status)
        self.assertEqual(job_status["user_id"], user_id)
        self.assertEqual(job_status["project_id"], project_id)
        self.assertEqual(job_status["prompt"], prompt)
        self.assertEqual(job_status["state"], ModificationState.CONTEXT_BUILDING)

    def test_update_job_state(self):
        """
        Test that the job state can be updated.
        """
        job_id = "test_job_123"
        self.service.modification_jobs[job_id] = {"state": ModificationState.IDLE}

        self.service.update_job_state(
            job_id, ModificationState.DONE, {"result": "success"}
        )

        job_status = self.service.get_job_status(job_id)
        self.assertEqual(job_status["state"], ModificationState.DONE)
        self.assertEqual(job_status["result"], "success")


if __name__ == "__main__":
    unittest.main()
