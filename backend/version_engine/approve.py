from version_engine.manifest_writer import apply_version_entry
from version_engine.md_writer import write_md_block
from version_engine.history_writer import append_to_history
from version_engine.changelog_writer import append_to_changelog
from version_engine.pending_writer import delete_pending_version

def approve_version(payload: dict):
    """
    Full integration: applies an approved version payload to all logs.
    """
    file = payload["file"]
    version = payload["version"]

    # Step 1: Update version manifest
    apply_version_entry(payload)

    # Step 2: Update markdown block (.md)
    write_md_block(payload)

    # Step 3: Append to file-based history
    append_to_history(payload)

    # Step 4: Append to global CHANGELOG
    append_to_changelog(payload)

    # Step 5: Remove from pending queue
    delete_pending_version(file, version)

    print(f"[✅] Version {version} approved for: {file}")
