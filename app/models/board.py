from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, List

from pydantic import BaseModel
from sqlmodel import Field, Relationship, SQLModel

from app.models.board_participant import BoardParticipant

if TYPE_CHECKING:
    from app.models.task import Task
    from app.models.user import User


def utcnow() -> datetime.datetime:
    return datetime.datetime.now(datetime.UTC)


class Board(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    created_at: datetime.datetime = Field(default_factory=utcnow)
    updated_at: datetime.datetime = Field(default_factory=utcnow)

    tasks: list["Task"] = Relationship(back_populates="board")
    participants: list["User"] = Relationship(
        back_populates="boards",
        link_model=BoardParticipant,
    )


class BaseBoard(BaseModel):
    name: str


class CreateBoard(BaseBoard):
    pass


class UpdateBoard(BaseBoard):
    name: str
    updated_at: datetime.datetime

    class Config:
        from_attributes = True


class ReadBoard(BaseBoard):
    id: int
    created_at: datetime.datetime
