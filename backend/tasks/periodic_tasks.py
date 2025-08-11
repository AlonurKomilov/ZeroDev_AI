# This file will contain Celery tasks that run on a schedule.
from backend.core.celery_app import celery_app
from backend.agents.feedback_analysis_agent import feedback_analysis_agent

@celery_app.task
def run_feedback_analysis():
    """
    Periodic task to run the feedback analysis agent.
    """
    print("Triggering periodic feedback analysis.")
    feedback_analysis_agent.run_analysis()
    return {"status": "Feedback analysis complete."}
