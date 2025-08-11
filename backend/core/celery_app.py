from celery import Celery
from backend.core.settings import settings

# Define the include list for tasks
# This tells Celery where to find task modules.
include_tasks = ["backend.tasks.parsing"]

celery_app = Celery(
    "worker",  # The name of the celery app
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=include_tasks
)

celery_app.conf.update(
    task_track_started=True,
    # It's good practice to have task-specific settings here
    # rather than in the main settings file if they are celery-specific.
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='UTC',
    enable_utc=True,
)
