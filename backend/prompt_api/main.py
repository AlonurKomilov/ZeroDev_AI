"""FastAPI service that converts a plain-language prompt into
structured project specs (JSON) using OpenAI Chat Completions."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# ✅ Import other API routers
from prompt_api.analyze import router as analyze_router
from prompt_api.suggest import router as suggest_router
from prompt_api.feedback import router as feedback_router

# ✅ Import shared OpenAI client
from .shared import client

# ✅ Create FastAPI app
app = FastAPI(title="ZeroDev Prompt Intake API", version="0.1.0")


# ✅ Route: Simple prompt → JSON spec (gpt-4o-mini)
class PromptRequest(BaseModel):
    prompt: str = Field(..., example="Build me a Telegram bot that echoes messages.")


class ProjectSpec(BaseModel):
    project_name: str
    description: str
    targets: list[str]


@app.post("/parse", response_model=ProjectSpec)
async def parse_prompt(req: PromptRequest) -> ProjectSpec:
    try:
        completion = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an assistant that converts software-project requests "
                        "into a JSON spec with keys: project_name, description, targets."
                    ),
                },
                {"role": "user", "content": req.prompt},
            ],
            response_format={
                "type": "json_object",
                "schema": {
                    "project_name": "string",
                    "description": "string",
                    "targets": {"type": "array", "items": "string"},
                },
            },
        )
        return ProjectSpec.model_validate_json(completion.choices[0].message.content)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


# ✅ Mount other routers
app.include_router(analyze_router)
app.include_router(suggest_router)
app.include_router(feedback_router)
