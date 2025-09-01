"""Generate actual project source files from ProjectSpec using GPT-4o."""

from __future__ import annotations

import os
from pathlib import Path

from openai import AsyncOpenAI

from backend.models.spec_model import ProjectSpec

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def generate_code_from_spec(spec: ProjectSpec, out_dir: Path) -> None:
    print(f"🤖 Generating code for: {spec.project_name}…")
    out_dir.mkdir(parents=True, exist_ok=True)

    system_msg = (
        "You are a senior developer. Generate a complete project in "
        f"{spec.language} from this spec. Include FastAPI if applicable. "
        "Make sure to always include an OpenAPI-compliant `/docs`, `/ping`, and `/openapi.json` endpoint."
    )
    prompt = (
        f"Project Description: {spec.description}\n"
        f"Targets: {', '.join(spec.targets)}\n\n"
        f"Output all files in this format:```\n"
        f"FILE: main.py\n<contents>\nFILE: tests/test_main.py\n<contents>\n```"
    )

    completion = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt},
        ],
    )

    content = completion.choices[0].message.content or ""
    log_path = out_dir / "codegen.log"
    log_path.write_text(content, encoding="utf-8")
    print(f"📝 Codegen log saved to: {log_path}")

    # Parse the FILE blocks from response
    files = content.split("FILE:")
    for block in files[1:]:
        header, *body_lines = block.strip().splitlines()
        filename = header.strip()
        body = "\n".join(body_lines).strip()
        file_path = out_dir / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(body, encoding="utf-8")
        print(f"✅ Generated: {file_path}")
