from __future__ import annotations

import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel
from sqlmodel import Field, Relationship, SQLModel


def utcnow() -> datetime.datetime:
    return datetime.datetime.now(datetime.UTC)


class Status(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: str | None = Field(default="")
    created_at: datetime.datetime = Field(default_factory=utcnow)
    updated_at: datetime.datetime = Field(default_factory=utcnow)
    status: Status = Field(default=Status.TODO)

    # Relationships to User
    author_id: Optional[int] = Field(default=None, foreign_key="user.id")
    author: Optional["User"] = Relationship(back_populates="tasks_authored")

    # Single assignee (optional)
    assignee_id: Optional[int] = Field(default=None, foreign_key="user.id")
    assignee: Optional["User"] = Relationship(back_populates="tasks_assigned")

    # Relationship to Board
    board_id: Optional[int] = Field(default=None, foreign_key="board.id")
    board: Optional["Board"] = Relationship(back_populates="tasks")


class BaseTask(BaseModel):
    name: str
    description: str
    status: Status
    assignee_id: Optional[int] = None


class CreateTask(BaseTask):
    author_id: Optional[int] = None
    board_id: Optional[int] = None


class UpdateTask(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[Status] = None
    assignee_id: Optional[int] = None
    board_id: Optional[int] = None
    updated_at: datetime.datetime = utcnow()

    class Config:
        from_attributes = True


class ReadTask(BaseTask):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    author_id: Optional[int] = None
    board_id: Optional[int] = None


# Forward references for type checkers / IDEs
from app.models.board import Board  # noqa: E402
from app.models.user import User  # noqa: E402
