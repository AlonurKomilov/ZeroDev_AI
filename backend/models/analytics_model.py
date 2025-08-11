from sqlmodel import SQLModel, Field
from typing import Optional

class PromptFeedback(SQLModel, table=True):
    """
    Stores aggregated feedback for prompt suggestions to identify which ones are effective.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    # A hash of the original prompt to group suggestions
    original_prompt_hash: str = Field(index=True)
    suggested_prompt: str
    upvotes: int = Field(default=0)
    downvotes: int = Field(default=0)

class SecurityViolationPattern(SQLModel, table=True):
    """
    Stores counts of different security violation types to identify common risky patterns.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    violation_type: str = Field(index=True, unique=True)
    count: int = Field(default=0)
