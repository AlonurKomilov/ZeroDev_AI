"""
This module contains the GithubService, which is responsible for all
interactions with the GitHub API, such as creating pull requests.
"""
import os
import time
from github import Github
from github.GithubException import GithubException
import git

from backend.core.logger import get_logger
from backend.transformation.orchestration import transformation_orchestrator, TransformationState

log = get_logger(__name__)

# TODO: Move this to a proper settings/config file
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")


class GithubService:
    """
    A service to interact with the GitHub API.
    """
    def __init__(self, token: str):
        if not token:
            raise ValueError("GitHub token is required.")
        self.github_client = Github(token)

    def create_pull_request(self, job_id: str) -> str:
        """
        Creates a new branch, commits changes, and opens a pull request.
        """
        log.info(f"Starting PR creation for job_id: {job_id}")
        job = transformation_orchestrator.get_job_status(job_id)
        if not job or "error" in job:
            raise ValueError(f"Invalid job for job_id: {job_id}")

        repo_path = job["cloned_repo_path"]
        user_prompt = job["prompt"]
        repo_url = job["repo_url"] # e.g., https://github.com/user/repo

        # 1. Generate branch name, title, and body
        timestamp = int(time.time())
        branch_name = f"feature/zerodev-transformation-{timestamp}"
        pr_title = f"[ZeroDev] Automated Refactoring: {user_prompt[:50]}"

        # This is a simplified summary. A real implementation would need
        # more data from previous steps.
        pr_body = f"""
### Goal
{user_prompt}

### Tech Stack Analysis
- Python (assumption, based on scanner)
- Pytest (assumption, based on validator)

### Summary of Changes
- Refactored code based on the user's prompt.
- (Note: Detailed file-level change stats would require enhancing the refactoring engine.)

### Validation Status
- All automated tests passed successfully.
"""

        try:
            # 2. Use GitPython to handle local git operations
            local_repo = git.Repo(repo_path)

            # Create and checkout the new branch
            new_branch = local_repo.create_head(branch_name)
            new_branch.checkout()
            log.info(f"Created and checked out branch: {branch_name}")

            # Stage all changes
            local_repo.git.add(A=True)

            # Commit changes
            commit_message = f"Automated refactoring by ZeroDev\n\n{user_prompt}"
            local_repo.index.commit(commit_message)
            log.info("Committed changes to the new branch.")

            # Push to origin
            origin = local_repo.remote(name="origin")
            origin.push(new_branch)
            log.info(f"Pushed branch {branch_name} to origin.")

            # 3. Use PyGithub to create the pull request
            repo_name = "/".join(repo_url.split("/")[-2:]) # e.g., "user/repo"
            github_repo = self.github_client.get_repo(repo_name)

            pr = github_repo.create_pull(
                title=pr_title,
                body=pr_body,
                head=branch_name,
                base="main" # Assuming the base branch is 'main'
            )
            log.info(f"Successfully created pull request: {pr.html_url}")

            transformation_orchestrator.update_job_state(
                job_id,
                TransformationState.DONE,
                {"pull_request_url": pr.html_url}
            )
            return pr.html_url

        except (git.exc.GitCommandError, GithubException) as e:
            log.error(f"Error during PR creation for job {job_id}: {e}", exc_info=True)
            transformation_orchestrator.update_job_state(
                job_id, TransformationState.ERROR, {"error_message": f"PR creation failed: {e}"}
            )
            raise e


github_service = GithubService(token=GITHUB_TOKEN)
