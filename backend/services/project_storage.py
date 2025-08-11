import uuid
import shutil
from pathlib import Path

class ProjectStorageService:
    """
    Manages the file system for user projects.
    """
    BASE_PATH = Path("workspace/projects")

    def get_project_path(self, user_id: uuid.UUID, project_id: uuid.UUID) -> Path:
        """
        Returns the path to a project's directory.
        """
        return self.BASE_PATH / str(user_id) / str(project_id)

    def create_project_dir(self, user_id: uuid.UUID, project_id: uuid.UUID) -> Path:
        """
        Creates a directory for a new project.
        """
        project_path = self.get_project_path(user_id, project_id)
        project_path.mkdir(parents=True, exist_ok=True)
        return project_path

    def delete_project_dir(self, user_id: uuid.UUID, project_id: uuid.UUID):
        """
        Deletes a project's directory.
        """
        project_path = self.get_project_path(user_id, project_id)
        if project_path.exists() and project_path.is_dir():
            shutil.rmtree(project_path)

project_storage_service = ProjectStorageService()
