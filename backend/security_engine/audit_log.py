import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any

LOG_FILE_PATH = Path("security_log.json")
MAX_LOG_ENTRIES = 1000
ENABLE_DEDUPLICATION = True


class AuditLogger:
    """Simple audit logger for security events"""
    
    def __init__(self, log_file: Optional[Path] = None):
        self.log_file = log_file or LOG_FILE_PATH
    
    async def log_event(self, event_type: str, data: Dict[str, Any]):
        """Log a security event"""
        try:
            # For now, just log to file
            # In production, this would send to proper audit system
            with open(self.log_file, "a") as f:
                log_entry = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "event_type": event_type,
                    "data": data
                }
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            print(f"Error logging audit event: {e}")


def clean_sensitive_data(prompt: str) -> str:
    """
    Replace sensitive info like passwords or credit card numbers.
    """
    prompt = re.sub(r"(?i)(password\s*=\s*[\'\"].+?[\'\"])", "password=***", prompt)
    prompt = re.sub(r"\b\d{16}\b", "****-****-****-****", prompt)
    return prompt


def hash_prompt(prompt: str) -> str:
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()


def log_violation(
    prompt: str,
    analysis_result: Dict,
    user_id: Optional[str] = None,
    test_mode: bool = False,
):
    """
    Save blocked/risky prompt to the log file with timestamp and details.
    Automatically avoids duplicates and truncates if too long.
    """

    safe_prompt = clean_sensitive_data(prompt)
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": user_id or "anonymous",
        "status": analysis_result["status"],
        "prompt": safe_prompt,
        "violations": analysis_result.get("violations", []),
        "hash": hash_prompt(safe_prompt),
    }

    log_file = Path("test_log.json") if test_mode else LOG_FILE_PATH

    existing_logs = []

    if log_file.exists():
        with open(log_file, "r", encoding="utf-8") as f:
            try:
                existing_logs = json.load(f)
            except json.JSONDecodeError:
                existing_logs = []

    # De-duplication check
    if ENABLE_DEDUPLICATION:
        if any(e.get("hash") == log_entry["hash"] for e in existing_logs):
            print("[⚠️] Duplicate prompt, not logging again.")
            return

    # Append new log
    existing_logs.append(log_entry)

    # Trim if too long
    if len(existing_logs) > MAX_LOG_ENTRIES:
        existing_logs = existing_logs[-MAX_LOG_ENTRIES:]

    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(existing_logs, f, indent=2)

    print(f"[🛡] Logged {log_entry['status']} prompt for user {log_entry['user_id']}")


def view_recent_logs(n: int = 10, test_mode: bool = False):
    """
    Print last n entries from log.
    """
    log_file = Path("test_log.json") if test_mode else LOG_FILE_PATH

    if not log_file.exists():
        print("[ℹ️] No log file found.")
        return

    with open(log_file, "r", encoding="utf-8") as f:
        try:
            logs = json.load(f)
            for entry in logs[-n:]:
                print(
                    f"{entry['timestamp']} | {entry['status'].upper()} | {entry['user_id']} → {entry['prompt']}"
                )
        except Exception as e:
            print(f"[❌] Failed to load log file: {e}")
