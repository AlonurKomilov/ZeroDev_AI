import json
from pathlib import Path
from typing import Dict

# Paths
MANIFEST_PATH = Path("version_manifest.json")
HISTORY_DIR = Path("version_engine/history")


def load_manifest() -> Dict:
    if MANIFEST_PATH.exists():
        with MANIFEST_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_manifest(data: Dict):
    with MANIFEST_PATH.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        print("[✔] Updated: version_manifest.json")


def apply_version_entry(payload: Dict):
    """
    Adds or updates a version entry in version_manifest.json and stores history JSON
    """
    file = payload["file"]
    version = payload["version"]
    updated = payload.get("updated")
    features = payload.get("features", [])
    next_steps = payload.get("next", [])

    manifest = load_manifest()
    if file not in manifest:
        manifest[file] = {"current": version, "history": []}

    # Add to history if new
    history_entry = {
        "version": version,
        "updated": updated,
        "features": features,
        "next": next_steps,
    }

    manifest[file]["current"] = version
    manifest[file]["history"].append(history_entry)

    save_manifest(manifest)

    # Also save individual file history (optional)
    file_id = file.replace("/", "__")
    history_path = HISTORY_DIR / f"{file_id}.json"
    with history_path.open("w", encoding="utf-8") as f:
        json.dump(manifest[file]["history"], f, indent=2)
        print(f"[✔] Saved: {history_path.name}")
