from pathlib import Path
from typing import Dict

# Map file categories to their corresponding markdown docs
CATEGORY_MD_MAP = {
    "agents/": "docs/AGENT_VERSIONS.md",
    "dashboard/": "docs/DASHBOARD_VERSIONS.md",
    "components/": "docs/FRONTEND_COMPONENTS.md",
    "prompt_api/": "docs/API_VERSIONS.md",
    "models/": "docs/MODEL_VERSIONS.md",
    "security_engine/": "docs/SECURITY_VERSIONS.md",
    "tests/": "docs/TEST_VERSIONS.md",
    "cli/": "docs/CLI_VERSIONS.md",
}

def write_md_block(payload: Dict):
    file_path = payload["file"]
    version = payload["version"]
    features = payload.get("features", [])
    next_steps = payload.get("next", [])
    updated = payload.get("updated", "unknown")

    # Determine which .md file this entry belongs to
    md_path = None
    for key, path in CATEGORY_MD_MAP.items():
        if file_path.startswith(key):
            md_path = Path(path)
            break

    if not md_path:
        print(f"[!] No mapped markdown file for: {file_path}")
        return

    # Load existing .md content
    content = ""
    if md_path.exists():
        content = md_path.read_text(encoding="utf-8")

    block_header = f"## {file_path} — {version}"
    block_body = f"""\
{block_header}
- Features: {", ".join(features)}
- Last Updated: {updated}

🔜 Next:
- {chr(10).join(f'- {item}' for item in next_steps)}

---
"""

    # Replace existing version block or append if not found
    if block_header in content:
        lines = content.splitlines()
        new_lines = []
        skip = False
        for line in lines:
            if line.strip().startswith(f"## {file_path} —"):
                skip = True
            if not skip:
                new_lines.append(line)
            if skip and line.strip() == "---":
                skip = False
        new_lines.append(block_body.strip())
        content = "\n".join(new_lines)
    else:
        content += "\n\n" + block_body.strip()

    md_path.write_text(content.strip(), encoding="utf-8")
    print(f"[✔] Markdown updated: {md_path.name}")
