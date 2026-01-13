from __future__ import annotations

from sqlmodel import Field, SQLModel


class BoardParticipant(SQLModel, table=True):
    """
    Link table for the many-to-many relationship between Board and User.

    This model intentionally lives in its own module to avoid cyclic runtime imports
    between `app.models.board` and `app.models.user`.
    """

    board_id: int = Field(foreign_key="board.id", primary_key=True)
    user_id: int = Field(foreign_key="user.id", primary_key=True)
