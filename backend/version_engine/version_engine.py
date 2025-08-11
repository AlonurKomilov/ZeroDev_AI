import json
from pathlib import Path
from datetime import datetime
from typing import List, Optional

# Constants
VERSION_MANIFEST = Path("version_manifest.json")
HISTORY_DIR = Path("version_engine/history")
PENDING_DIR = Path("version_engine/pending")

# Create dirs if not exist
HISTORY_DIR.mkdir(parents=True, exist_ok=True)
PENDING_DIR.mkdir(parents=True, exist_ok=True)

def update_version_log(
    file: str,
    version: str,
    features: List[str],
    next: Optional[List[str]] = None,
    updated: Optional[str] = None,
    status: str = "pending"
):
    """
    Main version updater — logs a version entry for a file and prepares it for approval.

    Args:
        file (str): relative path to the file (e.g. 'agents/ci_cd_agent.py')
        version (str): version string, e.g. 'v2.0.0'
        features (List[str]): list of features in this version
        next (List[str]): TODO or upcoming items
        updated (str): override update date (default: today)
        status (str): 'pending', 'approved', etc.
    """
    updated = updated or datetime.utcnow().strftime('%Y-%m-%d')
    file_id = file.replace("/", "__")

    payload = {
        "file": file,
        "version": version,
        "features": features,
        "next": next or [],
        "updated": updated,
        "status": status,
        "submitted_at": datetime.utcnow().isoformat()
    }

    # Save to pending folder for approval
    pending_file = PENDING_DIR / f"{file_id}__{version}.json"
    with pending_file.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    print(f"[✔] Version log submitted: {pending_file}")
    return payload
