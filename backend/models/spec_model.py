"""Shared project spec model used by Prompt API and CodeGen Agent."""
from __future__ import annotations

from pydantic import BaseModel, Field, validator
from typing import List
import re

class ProjectSpec(BaseModel):
    project_name: str = Field(..., example="telegram_echo_bot")
    description: str = Field(..., example="A Telegram bot that echoes user messages")
    language: str = Field(..., example="python")
    targets: List[str] = Field(..., example=["telegram bot", "echo feature", "test file"])

    @validator("project_name")
    def validate_project_name(cls, v):
        if not re.match(r"^[a-zA-Z0-9_\-]+$", v):
            raise ValueError("Project name contains invalid characters. Use only letters, numbers, hyphens, or underscores.")
        return v

    class Config:
        extra = "ignore"
        populate_by_name = True
