"""
Main FastAPI application for the ZeroDev Backend.
This file initializes the FastAPI app, includes all the API routers,
and sets up middleware.
"""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

# ✅ Import core services
from backend.core.logger import get_logger
from backend.core.celery_app import celery_app
from backend.tasks.parsing import parse_prompt_task

# ✅ Import API routers from the new `api` directory
from backend.api import analyze, suggest, feedback, admin_feedback, auth, projects, keys, templates, export, modify_api, review_api, emergency, dashboard, migration

# ✅ Import Prometheus monitoring components
from starlette_exporter import PrometheusMiddleware, handle_metrics
from prometheus_client import Counter

# ✅ Initialize logger
# This should be one of the first things to run
log = get_logger(__name__)

# ✅ Import middleware
from backend.core.middleware import GlobalStatusMiddleware

# ✅ Create FastAPI app
app = FastAPI(
    title="ZeroDev Backend API",
    version="2.0.0",
    description="The core API for the ZeroDev platform, built for stability and performance."
)

# ✅ Add global status middleware
app.add_middleware(GlobalStatusMiddleware)

# ✅ Add Prometheus middleware
app.add_middleware(PrometheusMiddleware)

# ✅ Define custom metrics
CELERY_TASKS_TOTAL = Counter(
    "zerodev_celery_tasks_total",
    "Total number of Celery tasks dispatched.",
    ["task_name"]
)

# ✅ Add metrics endpoint
app.add_route("/metrics", handle_metrics)

# ✅ Pydantic Models for the /parse endpoint
class PromptRequest(BaseModel):
    prompt: str = Field(..., example="Build me a Telegram bot that echoes messages.")
    model_name: str = Field("gpt-4o-mini", description="The name of the model to use for parsing.")

class TaskResponse(BaseModel):
    task_id: str

# Note: ProjectSpec is defined in models/spec_model.py, but the /parse endpoint no longer returns it directly.

@app.post("/parse", response_model=TaskResponse, status_code=202, tags=["Core"])
async def parse_prompt(req: PromptRequest) -> TaskResponse:
    """
    Accepts a prompt and dispatches it to a Celery worker for processing.
    Returns a task ID for the client to poll.
    """
    log.info(f"Dispatching prompt to Celery task for model {req.model_name}: {req.prompt[:50]}...")
    task = parse_prompt_task.delay(prompt=req.prompt, model_name=req.model_name)
    CELERY_TASKS_TOTAL.labels(task_name=parse_prompt_task.name).inc()
    log.info(f"Task {task.id} created for prompt using model {req.model_name}.")
    return TaskResponse(task_id=task.id)


@app.get("/tasks/{task_id}", tags=["Core"])
async def get_task_status(task_id: str):
    """
    Retrieves the status and result of a Celery task.
    """
    log.debug(f"Checking status for task {task_id}")
    task_result = celery_app.AsyncResult(task_id)

    response = {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result,
    }

    if task_result.failed():
        log.warning(f"Task {task_id} failed. Result: {task_result.result}")
        response["result"] = {
            "error": "Task failed.",
            "details": str(task_result.result),
        }

    return response


# ✅ Mount all API routers
log.info("Mounting API routers.")
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(keys.router, prefix="/api/keys", tags=["API Keys"])
app.include_router(templates.router, prefix="/api/templates", tags=["Templates"])
app.include_router(export.router, prefix="/api", tags=["Export"])
app.include_router(analyze.router, prefix="/prompt", tags=["Prompt Analysis"])
app.include_router(suggest.router, prefix="/prompt", tags=["Prompt Analysis"])
app.include_router(feedback.router, prefix="/feedback", tags=["User Feedback"])
app.include_router(admin_feedback.router, prefix="/admin", tags=["Admin"])
app.include_router(modify_api.router, prefix="/api/modify", tags=["Modification"])
app.include_router(review_api.router, prefix="/api/review", tags=["Review"])
app.include_router(emergency.router, prefix="/api/emergency", tags=["Emergency"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(migration.router, prefix="/api/migration", tags=["Migration"])

@app.get("/", tags=["Health"])
def read_root():
    """A simple health check endpoint."""
    return {"status": "ok", "message": "Welcome to ZeroDev Backend API"}
