import datetime
from typing import List

from pydantic import BaseModel
from sqlmodel import Field, Relationship, SQLModel

from app.models.task import Task


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    created_at: datetime.datetime = Field(default=datetime.datetime.now)
    updated_at: datetime.datetime = Field(default=datetime.datetime.now)

    tasks: List["Task"] = Relationship(back_populates="User")


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
