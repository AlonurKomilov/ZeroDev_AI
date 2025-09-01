import shutil
import uuid
from pathlib import Path

from backend.core.celery_app import celery_app
from backend.services.project_storage import project_storage_service


@celery_app.task
def create_project_files_task(user_id: str, project_id: str):
    """
    Celery task to create project files.
    For now, it just creates the project directory.
    """
    project_storage_service.create_project_dir(
        uuid.UUID(user_id), uuid.UUID(project_id)
    )
    return {"status": "created", "project_id": project_id}


@celery_app.task
def update_project_files_task(user_id: str, project_id: str, files: dict):
    """
    Celery task to update project files.
    This is a placeholder for now.
    """
    # In the future, this task will write the file contents to the project directory.
    return {
        "status": "updated",
        "project_id": project_id,
        "files_updated": list(files.keys()),
    }


@celery_app.task
def delete_project_files_task(user_id: str, project_id: str):
    """
    Celery task to delete project files.
    """
    project_storage_service.delete_project_dir(
        uuid.UUID(user_id), uuid.UUID(project_id)
    )
    return {"status": "deleted", "project_id": project_id}


@celery_app.task
def export_project_zip_task(user_id: str, project_id: str) -> str:
    """
    Celery task to export a project as a zip file.
    Returns the path to the zip file.
    """
    project_path = project_storage_service.get_project_path(
        uuid.UUID(user_id), uuid.UUID(project_id)
    )

    # Create a temporary directory for the zip file
    export_dir = Path("workspace/exports")
    export_dir.mkdir(exist_ok=True)

    zip_path = export_dir / f"{project_id}.zip"

    shutil.make_archive(str(zip_path.with_suffix("")), "zip", str(project_path))

    return str(zip_path)
