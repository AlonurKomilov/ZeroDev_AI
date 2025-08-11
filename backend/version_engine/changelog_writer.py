changelog_writer.pyfrom pathlib import Path
from typing import Dict, List

CHANGELOG_PATH = Path("CHANGELOG.md")

def format_changelog_block(file: str, version: str, updated: str, features: List[str]) -> str:
    lines = [
        f"## [{version}] — {updated}",
        f"### {file}"
    ]
    for feat in features:
        lines.append(f"- {feat}")
    lines.append("")  # For spacing
    return "\n".join(lines)

def append_to_changelog(payload: Dict):
    file = payload["file"]
    version = payload["version"]
    updated = payload.get("updated", "unknown")
    features = payload.get("features", [])

    block = format_changelog_block(file, version, updated, features)

    if CHANGELOG_PATH.exists():
        existing = CHANGELOG_PATH.read_text(encoding="utf-8")
        if block in existing:
            print(f"[ℹ️] Entry already exists in CHANGELOG.md for: {file} {version}")
            return

    with CHANGELOG_PATH.open("a", encoding="utf-8") as f:
        f.write("\n" + block)
        print(f"[📝] Appended to CHANGELOG.md")
