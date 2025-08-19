"""
This module contains the RefactoringEngine, which is the "brain" of the
transformation process. It uses an LLM to generate code modifications.
"""

import json
import os

from backend.core.ai_router import get_llm_adapter
from backend.core.logger import get_logger
from backend.transformation.orchestration import (
    TransformationState,
    transformation_orchestrator,
)

log = get_logger(__name__)


class RefactoringEngine:
    """
    The engine that performs code refactoring using an LLM.
    """

    async def refactor(self, job_id: str):
        log.info(f"Starting refactoring for job_id: {job_id}")
        job = transformation_orchestrator.get_job_status(job_id)
        if not job or "error" in job:
            log.error(f"Invalid job for job_id: {job_id}")
            return

        prompt = job["prompt"]
        repo_path = job["cloned_repo_path"]
        try:
            architecture_map = json.loads(job["architecture_map"])
        except (json.JSONDecodeError, TypeError):
            log.error(f"Invalid or missing architecture_map for job_id: {job_id}")
            transformation_orchestrator.update_job_state(
                job_id,
                TransformationState.ERROR,
                {"error_message": "Invalid architecture map."},
            )
            return

        # For simplicity, we'll just include the top 10 files in the prompt.
        # A more advanced implementation would select files more intelligently.
        files_to_include = list(architecture_map.keys())[:10]
        file_contents = {}
        for file in files_to_include:
            try:
                with open(os.path.join(repo_path, file), "r", encoding="utf-8") as f:
                    file_contents[file] = f.read()
            except Exception as e:
                log.warning(f"Could not read file {file}: {e}")

        system_prompt = """
You are an expert software engineer AI. Your task is to perform a code transformation on an existing codebase based on a user's request.

You will be given:
1. The user's high-level goal.
2. A map of the project's architecture (files, classes, functions).
3. The contents of the most relevant files.

Your instructions are:
- Analyze the request and the provided code.
- Generate the complete, updated source code for every file that needs to be changed.
- You MUST provide the full content of the file, not just a diff.
- Your response MUST be a JSON object where keys are the file paths and values are the new code content as a string.
- Example: {"src/main.py": "import os\\n\\nprint('Hello, World!')"}
- Do not include any files that do not need to be changed.
- Ensure the new code is syntactically correct and aligns with the user's request.
"""

        user_prompt = f"""
**User's Goal:**
{prompt}

**Project Architecture Map:**
{json.dumps(architecture_map, indent=2)}

**Relevant File Contents:**
{json.dumps(file_contents, indent=2)}

Please provide the refactored code in the specified JSON format.
"""

        try:
            adapter = get_llm_adapter("gpt-4o-mini")
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
            response_format = {"type": "json_object"}

            completion = await adapter.chat_completion(
                messages=messages, model="gpt-4o-mini", response_format=response_format
            )

            response_json_str = completion["choices"][0]["message"]["content"]
            refactored_files = json.loads(response_json_str)

            log.info(f"LLM generated refactoring for {len(refactored_files)} files.")

            # Apply the changes to the cloned repository
            for file_path, new_content in refactored_files.items():
                full_path = os.path.join(repo_path, file_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                log.info(f"Applied refactoring to {file_path}")

            transformation_orchestrator.update_job_state(
                job_id, TransformationState.VALIDATING
            )
            log.info(f"Refactoring complete for job {job_id}. Moving to validation.")

            # Trigger the validation task
            from backend.transformation.tasks import validation_task

            validation_task.delay(job_id)

        except Exception as e:
            log.error(f"Error during refactoring for job {job_id}: {e}", exc_info=True)
            transformation_orchestrator.update_job_state(
                job_id,
                TransformationState.ERROR,
                {"error_message": f"Refactoring failed: {e}"},
            )


refactoring_engine = RefactoringEngine()
