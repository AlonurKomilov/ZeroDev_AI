from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, List, Optional

from fastapi_users_db_sqlmodel import SQLModelBaseUserDB  # type: ignore
from sqlalchemy.types import JSON  # type: ignore
from sqlmodel import Column, Field, Relationship  # type: ignore


class User(SQLModelBaseUserDB, table=True):  # type: ignore
    """
    Represents a user in the system.
    This model is compatible with FastAPI-Users and SQLModel.
    """

    __tablename__ = "users"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )

    # Add any additional user fields here.
    # For example:
    # first_name: str = Field(max_length=50)
    # last_name: str = Field(max_length=50)

    # Encrypted LLM API keys
    llm_api_keys: Optional[dict] = Field(default={}, sa_column=Column(JSON))

    # Relationship to projects
    projects: List["Project"] = Relationship(back_populates="user")


if TYPE_CHECKING:
    from backend.models.project_model import Project
