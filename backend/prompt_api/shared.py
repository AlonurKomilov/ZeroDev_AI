from __future__ import annotations

from openai import AsyncOpenAI
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("❌ OPENAI_API_KEY is missing. Please check your .env file.")

client = AsyncOpenAI(api_key=api_key)
