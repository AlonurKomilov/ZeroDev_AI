from __future__ import annotations
import uuid
import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from backend.models.user_model import User


class Project(SQLModel, table=True):
    """
    Represents a user's project.
    """
    __tablename__ = "projects"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    name: str = Field(index=True)
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

    # Foreign key to the User model
    user_id: uuid.UUID = Field(foreign_key="users.id")

    # Relationship to the User model
    user: "User" = Relationship(back_populates="projects")
