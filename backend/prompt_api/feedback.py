from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime
import json
import os

router = APIRouter()

LOG_PATH = "security_engine/feedback_log.json"

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

    # Append to file
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    if not os.path.exists(LOG_PATH):
        with open(LOG_PATH, "w") as f:
            json.dump([entry], f, indent=2)
    else:
        with open(LOG_PATH, "r+") as f:
            logs = json.load(f)
            logs.append(entry)
            f.seek(0)
            json.dump(logs, f, indent=2)

    return {"status": "ok", "message": "Feedback logged"}
