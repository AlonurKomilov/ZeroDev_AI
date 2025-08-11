import json
import time
from typing import Optional

from fastapi import APIRouter
from openai import OpenAIError
from pydantic import BaseModel

from security_engine.audit_log import log_violation
from security_engine.filters import analyze_prompt

# Use the shared OpenAI client
from .shared import client

router = APIRouter()


class AnalyzePromptRequest(BaseModel):
    prompt: str
    role: Optional[str] = "guest"
    user_id: Optional[str] = "anonymous"


# Dummy helper: tag classifier (can be replaced by AI model later)
def classify_prompt_type(prompt: str) -> str:
    prompt = prompt.lower()
    if "bot" in prompt:
        return "bot"
    elif "dashboard" in prompt or "web" in prompt:
        return "web_tool"
    elif "payment" in prompt or "credit card" in prompt:
        return "finance"
    elif "game" in prompt:
        return "game"
    return "general"


async def get_ai_suggestions(prompt: str, violation: dict) -> list[str]:
    """Generates helpful suggestions for a flagged prompt using an AI model."""
    if not client:
        return []

    keyword = violation.get("word") or violation.get("pattern", "")
    message = violation.get("message", "")

    try:
        system_prompt = (
            "You are an expert security assistant. A user's prompt was flagged. "
            "Your task is to provide 2-3 safe, alternative suggestions for how the user could "
            "rephrase their prompt to achieve a similar goal without triggering security filters. "
            "Return the suggestions as a JSON array of strings in a 'suggestions' key."
        )
        user_prompt = (
            f"The user's prompt was: '{prompt}'\n"
            f"It was flagged for the following reason: '{message}'\n"
            f"The keyword/pattern that triggered this was: '{keyword}'\n\n"
            "Please provide 2-3 safe, alternative suggestions."
        )

        completion = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
        )
        response_data = json.loads(completion.choices[0].message.content)
        return response_data.get("suggestions", [])
    except (OpenAIError, json.JSONDecodeError) as e:
        print(f"[⚠️] Could not generate AI suggestions: {e}")
        return []


def get_severity(score: int) -> str:
    if score >= 15:
        return "high"
    elif score >= 7:
        return "medium"
    return "low"


@router.post("/analyze", tags=["Prompt Filter"])
async def analyze_prompt_route(data: AnalyzePromptRequest):
    start = time.time()

    result = analyze_prompt(data.prompt, role=data.role)

    # Add AI-generated suggestions to each violation
    for v in result["violations"]:
        v["suggestions"] = await get_ai_suggestions(data.prompt, v)

    # Optional logging if not safe
    if result["status"] != "safe":
        log_violation(data.prompt, result, user_id=data.user_id)

    # Extend result with UX fields
    enriched_result = {
        "status": result["status"],
        "score": result["score"],
        "severity": get_severity(result["score"]),
        "violations": result["violations"],
        "prompt_type": classify_prompt_type(data.prompt),
        "eval_time_ms": int((time.time() - start) * 1000),
    }

    return enriched_result
