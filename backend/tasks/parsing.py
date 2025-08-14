import asyncio

from backend.core.ai_router import get_llm_adapter
from backend.core.celery_app import celery_app
from backend.core.logger import get_logger
from backend.models.spec_model import ProjectSpec

log = get_logger(__name__)


@celery_app.task(bind=True, name="tasks.parse_prompt")
def parse_prompt_task(self, prompt: str, model_name: str = "gpt-4o-mini") -> dict:
    """
    Celery task to parse a prompt using a specified language model via the AI router.
    The result must be a JSON-serializable dictionary.
    """
    log.info(f"Starting prompt parsing task with model: {model_name}")
    try:
        adapter = get_llm_adapter(model_name)

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an assistant that converts software-project requests "
                    "into a JSON spec with keys: project_name, description, targets."
                ),
            },
            {"role": "user", "content": prompt},
        ]

        response_format = {
            "type": "json_object",
            "schema": ProjectSpec.model_json_schema(),
        }

        # Get or create an event loop for the async call
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        completion = loop.run_until_complete(
            adapter.chat_completion(
                messages=messages, model=model_name, response_format=response_format
            )
        )

        spec_json_str = completion["choices"][0]["message"]["content"]
        project_spec = ProjectSpec.model_validate_json(spec_json_str)
        log.info(
            f"Successfully parsed prompt into spec for project: {project_spec.project_name}"
        )
        return project_spec.model_dump()
    except Exception as exc:
        log.error(f"Error in prompt parsing task: {exc}", exc_info=True)
        self.update_state(
            state="FAILURE",
            meta={"exc_type": type(exc).__name__, "exc_message": str(exc)},
        )
        raise exc
