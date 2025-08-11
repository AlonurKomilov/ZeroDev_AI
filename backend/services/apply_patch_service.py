import subprocess
import uuid
from pathlib import Path
from backend.services.project_storage import project_storage_service

class ApplyPatchService:
    """
    A service dedicated to safely applying a diff patch to the project files
    upon user approval.
    """

    def apply_patch(self, user_id: str, project_id: str, diff_patch: str) -> dict:
        """
        Applies a given patch to the main project files.

        This method should be called only after the patch has been reviewed and
        approved by the user.

        :param user_id: The ID of the user who owns the project.
        :param project_id: The ID of the project to be patched.
        :param diff_patch: The string containing the diff in unified format.
        :return: A dictionary indicating success or failure.
        """
        print(f"Applying approved patch to project: {project_id}")

        try:
            project_path = project_storage_service.get_project_path(uuid.UUID(user_id), uuid.UUID(project_id))
        except (ValueError, TypeError):
            return {"success": False, "error": "Invalid user_id or project_id format."}

        if not project_path.exists() or not project_path.is_dir():
            return {"success": False, "error": f"Project directory not found for project_id: {project_id}"}

        # Use a temporary name for the patch file to avoid conflicts.
        patch_file_path = project_path / f"tmp_{uuid.uuid4()}.patch"

        try:
            with open(patch_file_path, "w", encoding="utf-8") as f:
                f.write(diff_patch)

            # Use the 'patch' command-line utility to apply the diff.
            # The `-p1` argument strips the leading directory component (a/ or b/).
            # `cwd` ensures the command runs in the correct project directory.
            apply_command = ["patch", "-p1", "-i", str(patch_file_path)]
            result = subprocess.run(
                apply_command,
                cwd=project_path,
                capture_output=True,
                text=True,
                check=True  # Raises CalledProcessError on non-zero exit codes.
            )
            print(f"Patch applied successfully to project {project_id}.")
            if result.stdout:
                print(f"Patch output:\n{result.stdout}")
            return {"success": True}

        except FileNotFoundError:
            # This happens if the 'patch' command is not installed on the system.
            error_msg = "Error: The 'patch' command was not found. Please ensure it is installed and in the system's PATH."
            print(error_msg)
            return {"success": False, "error": error_msg}

        except subprocess.CalledProcessError as e:
            # This happens if the patch command fails (e.g., the patch is invalid or doesn't apply cleanly).
            error_msg = f"Failed to apply patch. The patch may be invalid or rejected.\nStderr: {e.stderr}"
            print(error_msg)
            return {"success": False, "error": error_msg}

        except Exception as e:
            # Catch any other unexpected errors.
            error_msg = f"An unexpected error occurred during patch application: {e}"
            print(error_msg)
            return {"success": False, "error": error_msg}

        finally:
            # Ensure the temporary patch file is always removed.
            if patch_file_path.exists():
                patch_file_path.unlink()

# Singleton instance of the service
apply_patch_service = ApplyPatchService()
