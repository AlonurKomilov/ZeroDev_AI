from fastapi import APIRouter, HTTPException
from pathlib import Path
import json

from backend.core.logger import get_logger

router = APIRouter()
log = get_logger(__name__)

# Define the log path relative to the project root
LOG_PATH = Path("backend/security_engine/feedback_log.json")

@router.get("/admin/feedback_logs", tags=["Admin"])
def get_feedback_logs():
    log.info("Admin request for feedback logs.")
    if not LOG_PATH.exists():
        log.warning(f"Feedback log file not found at: {LOG_PATH}")
        return []

    try:
        with LOG_PATH.open("r") as f:
            # Handle empty file case
            content = f.read()
            if not content:
                return []
            logs = json.loads(content)
        return logs
    except json.JSONDecodeError as e:
        log.error(f"Failed to parse feedback logs from {LOG_PATH}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to parse logs: {e}")
    except IOError as e:
        log.error(f"Failed to read feedback logs from {LOG_PATH}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to load logs: {e}")
