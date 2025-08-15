import datetime
import uuid

from pydantic import BaseModel


class ProjectBase(BaseModel):
    name: str


class ProjectCreate(ProjectBase):
    pass


class ProjectRead(ProjectBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True


class ProjectUpdate(ProjectBase):
    pass
