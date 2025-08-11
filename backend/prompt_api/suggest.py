from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
from openai import AsyncOpenAI
import os

router = APIRouter()

# Load API key from .env
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("❌ OPENAI_API_KEY is missing. Please check your .env file.")

ai = AsyncOpenAI(api_key=api_key)


class SuggestPromptRequest(BaseModel):
    prompt: str
    role: Optional[str] = "guest"
    user_id: Optional[str] = "anonymous"


def get_confidence_score(original: str, suggestion: str) -> float:
    original = original.lower().strip()
    suggestion = suggestion.lower().strip()
    shared = set(original.split()) & set(suggestion.split())
    score = len(shared) / max(len(original.split()), 1)
    return round(min(score + 0.2, 0.99), 2)


@router.post("/suggest_prompt", tags=["AI Suggestions"])
async def suggest_prompt_route(data: SuggestPromptRequest):
    system_msg = (
        "You are a smart AI assistant. "
        "When given an unsafe or unethical software prompt, rewrite it into 3 safe, ethical, and developer-friendly alternatives. "
        "For each variant, include a one-line explanation of why it's safe and how it's better. "
        "Format: Each variant on a new line, followed by its explanation in parentheses."
    )

    user_msg = f"Rewrite this software prompt in 3 safe and ethical ways:\n{data.prompt}"

    try:
        response = await ai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg}
            ],
            temperature=0.4
        )
    except Exception as e:
        return {"error": f"OpenAI API Error: {str(e)}"}

    raw_output = response.choices[0].message.content.strip()
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
