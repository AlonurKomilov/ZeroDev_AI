from version_engine.changelog_writer import append_to_changelog  # type: ignore
from version_engine.history_writer import (  # type: ignore
    load_file_history,
    save_file_history,
)
from version_engine.manifest_writer import load_manifest, save_manifest  # type: ignore
from version_engine.md_writer import write_md_block  # type: ignore


def rollback_version(file: str, target_version: str):
    """
    Reverts a file's version to a previous version from its history.
    """
    history = load_file_history(file)
    if not history:
        print(f"[!] No history found for: {file}")
        return

    entry = next((v for v in history if v["version"] == target_version), None)
    if not entry:
        print(f"[!] Version {target_version} not found in history for: {file}")
        return

    # Reorder history: bring the rollback version to the end (like re-approval)
    history = [v for v in history if v["version"] != target_version]
    history.append(entry)
    save_file_history(file, history)

    # Update version_manifest.json
    manifest = load_manifest()
    manifest[file]["current"] = target_version
    save_manifest(manifest)

    # Update .md block
    payload = {
        "file": file,
        "version": entry["version"],
        "updated": entry.get("updated"),
        "features": entry.get("features", []),
        "next": entry.get("next", []),
    }
    write_md_block(payload)
    append_to_changelog(payload)

    print(f"[⏪] Rolled back {file} to version {target_version}")
