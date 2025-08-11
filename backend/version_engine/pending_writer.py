import json
from pathlib import Path
from typing import Dict, List, Optional

PENDING_DIR = Path("version_engine/pending")
PENDING_DIR.mkdir(parents=True, exist_ok=True)

def get_pending_file_path(file: str, version: str) -> Path:
    file_id = file.replace("/", "__")
    return PENDING_DIR / f"{file_id}__{version}.json"

def save_pending_version(payload: Dict):
    """
    Stores a pending version entry for frontend approval.
    """
    file = payload["file"]
    version = payload["version"]
    path = get_pending_file_path(file, version)

    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"[📥] Pending version stored: {path.name}")

def load_all_pending() -> List[Dict]:
    """
    Loads all pending version requests.
    """
    entries = []
    for file in PENDING_DIR.glob("*.json"):
        with file.open("r", encoding="utf-8") as f:
            data = json.load(f)
            entries.append(data)
    return entries

def delete_pending_version(file: str, version: str):
    """
    Deletes the approved/rejected version entry from pending folder.
    """
    path = get_pending_file_path(file, version)
    if path.exists():
        path.unlink()
        print(f"[🗑️] Deleted pending entry: {path.name}")
    else:
        print(f"[!] Pending entry not found: {path.name}")
