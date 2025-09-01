from backend.core.settings import settings
from celery import Celery

# Define the include list for tasks
# This tells Celery where to find task modules.
include_tasks = [
    "backend.tasks.parsing",
    "backend.tasks.project_tasks",
    "backend.tasks.modification_tasks",
    "backend.tasks.periodic_tasks",
]

celery_app = Celery(
    "worker",  # The name of the celery app
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=include_tasks,
)

celery_app.conf.update(
    task_track_started=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)

# Celery Beat Schedule
# This configures the scheduler to run tasks at specified intervals.
celery_app.conf.beat_schedule = {
    "feedback-analysis-every-hour": {
        "task": "backend.tasks.periodic_tasks.run_feedback_analysis",
        "schedule": 3600.0,  # Run every hour
    },
}
