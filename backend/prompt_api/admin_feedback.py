from fastapi import APIRouter, HTTPException
import os
import json

router = APIRouter()

LOG_PATH = "security_engine/feedback_log.json"

@router.get("/admin/feedback_logs", tags=["Admin"])
def get_feedback_logs():
    if not os.path.exists(LOG_PATH):
        return []

    try:
        with open(LOG_PATH, "r") as f:
            logs = json.load(f)
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load logs: {str(e)}")
