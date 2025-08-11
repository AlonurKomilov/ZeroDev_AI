from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime
import json
from pathlib import Path

from backend.core.logger import get_logger

router = APIRouter()
log = get_logger(__name__)

# Define the log path relative to the project root
LOG_PATH = Path("backend/security_engine/feedback_log.json")

class FeedbackEntry(BaseModel):
    user_id: str
    suggested_prompt: str
    feedback: str  # "up" or "down"
    index: int
    original_prompt: str


@router.post("/feedback", tags=["AI Feedback"])
def submit_feedback(data: FeedbackEntry):
    entry = {
        "user_id": data.user_id,
        "feedback": data.feedback,
        "suggested_prompt": data.suggested_prompt,
        "original_prompt": data.original_prompt,
        "index": data.index,
        "timestamp": datetime.utcnow().isoformat()
    }

    log.info(f"Logging feedback for user {data.user_id}: {data.feedback}")

    try:
        # Ensure the directory exists
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

        if not LOG_PATH.exists():
            logs = []
        else:
            with LOG_PATH.open("r") as f:
                try:
                    logs = json.load(f)
                    if not isinstance(logs, list):
                        log.warning("feedback_log.json does not contain a list. Starting fresh.")
                        logs = []
                except json.JSONDecodeError:
                    log.warning("feedback_log.json is corrupted. Starting fresh.")
                    logs = []

        logs.append(entry)

        with LOG_PATH.open("w") as f:
            json.dump(logs, f, indent=2)

    except IOError as e:
        log.error(f"Failed to write feedback to {LOG_PATH}: {e}", exc_info=True)
        return {"status": "error", "message": "Could not log feedback."}

    return {"status": "ok", "message": "Feedback logged"}
