import json
from pathlib import Path
from typing import Dict, List

HISTORY_DIR = Path("version_engine/history")
HISTORY_DIR.mkdir(parents=True, exist_ok=True)


def load_file_history(file: str) -> List[Dict]:
    file_id = file.replace("/", "__")
    history_path = HISTORY_DIR / f"{file_id}.json"
    if history_path.exists():
        with history_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_file_history(file: str, history: List[Dict]):
    file_id = file.replace("/", "__")
    history_path = HISTORY_DIR / f"{file_id}.json"
    with history_path.open("w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)
    print(f"[✔] History saved: {history_path.name}")


def append_to_history(payload: Dict):
    """
    Appends a new version entry to the file's history JSON.
    """
    file = payload["file"]
    version = payload["version"]
    updated = payload.get("updated", "unknown")
    features = payload.get("features", [])
    next_steps = payload.get("next", [])

    history = load_file_history(file)

    entry = {
        "version": version,
        "updated": updated,
        "features": features,
        "next": next_steps,
    }

    history.append(entry)
    save_file_history(file, history)
