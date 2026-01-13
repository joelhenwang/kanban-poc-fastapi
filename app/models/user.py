from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, List

from pydantic import BaseModel
from sqlmodel import Field, Relationship, SQLModel

from app.models.board import BoardParticipant

if TYPE_CHECKING:
    from app.models.board import Board
    from app.models.task import Task


def utcnow() -> datetime.datetime:
    return datetime.datetime.now(datetime.UTC)


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    created_at: datetime.datetime = Field(default_factory=utcnow)
    updated_at: datetime.datetime = Field(default_factory=utcnow)

    # Tasks where this user is the author/creator
    tasks_authored: List["Task"] = Relationship(back_populates="author")

    # Tasks where this user is the assignee (single assignee per task)
    tasks_assigned: List["Task"] = Relationship(back_populates="assignee")
    boards: List["Board"] = Relationship(
        back_populates="participants", link_model=BoardParticipant
    )


class BaseUser(BaseModel):
    name: str


class CreateUser(BaseUser):
    pass


class UpdateUser(BaseUser):
    name: str
    updated_at: datetime.datetime

    class Config:
        from_attributes = True


class ReadUser(BaseUser):
    id: int
