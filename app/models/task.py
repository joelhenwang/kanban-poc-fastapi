import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel
from sqlmodel import Field, Relationship, SQLModel

from app.models.board import Board
from app.models.user import User


class Status(Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: str | None = Field(default="")
    created_at: datetime.datetime = Field(default=datetime.datetime.now)
    updated_at: datetime.datetime = Field(default=datetime.datetime.now)
    status: Status = Field(default=Status.TODO)

    author_id: Optional[int] = Field(default=None, foreign_key="user.id")
    author: User = Relationship(back_populates="tasks")

    board_id: Optional[int] = Field(default=None, foreign_key="board.id")
    board: Optional[Board] = Relationship(back_populates="tasks")


class BaseTask(BaseModel):
    name: str
    description: str
    status: Status


class CreateTask(BaseTask):
    pass


class UpdateTask(BaseTask):
    name: str
    description: str
    status: Status
    updated_at: datetime.datetime

    class Config:
        from_attributes = True


class ReadTask(BaseTask):
    id: int
    created_at: datetime.datetime
