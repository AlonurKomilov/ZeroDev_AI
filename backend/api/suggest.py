from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List

# Import centralized services
from backend.core.ai_router import get_llm_adapter
from backend.core.cache import cache
from backend.core.logger import get_logger

router = APIRouter()
log = get_logger(__name__)


class SuggestPromptRequest(BaseModel):
    prompt: str
    role: Optional[str] = "guest"
    user_id: Optional[str] = "anonymous"
    model_name: str = "gpt-4o"


def get_confidence_score(original: str, suggestion: str) -> float:
    original = original.lower().strip()
    suggestion = suggestion.lower().strip()
    shared = set(original.split()) & set(suggestion.split())
    score = len(shared) / max(len(original.split()), 1)
    return round(min(score + 0.2, 0.99), 2)


@router.post("/suggest_prompt", tags=["AI Suggestions"])
@cache(ttl=3600)  # Cache suggestions for 1 hour
async def suggest_prompt_route(data: SuggestPromptRequest):
    log.info(f"Generating suggestions for prompt using model {data.model_name}: {data.prompt[:50]}...")

    adapter = get_llm_adapter(data.model_name)

    system_msg = (
        "You are a smart AI assistant. "
        "When given an unsafe or unethical software prompt, rewrite it into 3 safe, ethical, and developer-friendly alternatives. "
        "For each variant, include a one-line explanation of why it's safe and how it's better. "
        "Format: Each variant on a new line, followed by its explanation in parentheses."
    )
    user_msg = f"Rewrite this software prompt in 3 safe and ethical ways:\n{data.prompt}"

    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_msg}
    ]

    try:
        response = await adapter.chat_completion(
            messages=messages,
            model=data.model_name,
            temperature=0.4
        )
    except Exception as e:
        log.error(f"LLM API Error during suggestion generation: {e}", exc_info=True)
        return {"error": f"LLM API Error: {str(e)}"}

    raw_output = response['choices'][0]['message']['content'].strip()
    lines = [line.strip("•- ").strip() for line in raw_output.split("\n") if line.strip()]
    top_3 = lines[:3] if len(lines) >= 3 else lines

    results = []
    for line in top_3:
        if "(" in line and line.endswith(")"):
            prompt_text, explanation = line.rsplit("(", 1)
            explanation = explanation.rstrip(")")
        else:
            prompt_text = line
            explanation = ""

        score = get_confidence_score(data.prompt, prompt_text)
        results.append({
            "suggested_prompt": prompt_text.strip(),
            "confidence": score,
            "explanation": explanation.strip()
        })

    return {
        "original_prompt": data.prompt,
        "role": data.role,
        "suggestions": results
    }
