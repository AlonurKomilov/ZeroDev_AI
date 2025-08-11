import os
import uuid
from pathlib import Path
from backend.services.project_storage import project_storage_service

class ContextBuilderAgent:
    """
    Builds the optimal context for modification tasks by retrieving
    conversation history and performing dependency analysis on the project's code
    to select the most relevant files for the task.
    """

    def build_context(self, user_id: str, project_id: str, prompt: str) -> dict:
        """
        Gathers context for a modification task.

        For this initial implementation, it simply retrieves all files from the
        project directory. Future implementations should perform more advanced
        analysis (e.g., dependency checking, embedding-based search) to select
        only the most relevant files.
        """
        print(f"Building context for project: {project_id}")

        try:
            # The user_id is required by the project_storage_service to locate the project directory.
            project_path = project_storage_service.get_project_path(uuid.UUID(user_id), uuid.UUID(project_id))
        except (ValueError, TypeError):
            # Handle cases where user_id or project_id are not valid UUIDs
            return {"error": "Invalid user_id or project_id format."}

        if not project_path.exists() or not project_path.is_dir():
            return {"error": f"Project directory not found for project_id: {project_id}"}

        context_files = {}

        for root, _, files in os.walk(project_path):
            for file in files:
                # We should add a filter here to exclude certain files and directories
                # (e.g., .git, __pycache__, node_modules, build artifacts)
                file_path = Path(root) / file
                relative_path = file_path.relative_to(project_path)

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    context_files[str(relative_path)] = content
                except Exception as e:
                    # This could happen for binary files or files with encoding issues.
                    print(f"Could not read file {file_path}: {e}")
                    context_files[str(relative_path)] = f"Error: Could not read file content. It may be a binary file. Details: {e}"

        print(f"Context built for project: {project_id}. Found {len(context_files)} files.")
        return context_files

# Singleton instance of the agent
context_builder_agent = ContextBuilderAgent()
