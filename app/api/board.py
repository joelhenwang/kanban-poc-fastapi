"""
Board API router.

This module exposes endpoints to manage Boards and to fetch Tasks that belong to a Board.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, Query, Response, status
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.board import Board, CreateBoard, ReadBoard, UpdateBoard
from app.models.task import ReadTask
from app.routers.board import (
    create_board,
    delete_board,
    get_board,
    get_board_with_tasks,
    update_board,
)

router = APIRouter(prefix="/boards", tags=["boards"])


@router.post(
    "",
    response_model=ReadBoard,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new board",
    description=(
        "Creates a new Board resource.\n\n"
        "Use this when you want a new container for tasks (a kanban board)."
    ),
)
def create_board_endpoint(
    payload: CreateBoard, session: Session = Depends(get_session)
):
    """
    Create a new board.

    - Input: `CreateBoard` (currently includes a `name`)
    - Output: the created board (`ReadBoard`)
    """
    return create_board(name=payload.name, session=session)


@router.get(
    "",
    response_model=List[ReadBoard],
    summary="List boards",
    description=(
        "Returns a paginated list of boards.\n\n"
        "Optional query:\n"
        "- `q`: filters by board name (substring match)\n"
        "- `offset`/`limit`: pagination controls"
    ),
)
def list_boards_endpoint(
    session: Session = Depends(get_session),
    offset: int = Query(0, ge=0, description="Number of records to skip (pagination)."),
    limit: int = Query(
        100, ge=1, le=500, description="Max records to return (pagination)."
    ),
    q: Optional[str] = Query(
        None, description="Optional name search (substring match)."
    ),
):
    """
    List boards with optional filtering and pagination.
    """
    query = select(Board)
    if q:
        query = query.where(Board.name.contains(q))  # pyright: ignore[reportAttributeAccessIssue]
    query = query.offset(offset).limit(limit)
    return list(session.exec(query).all())


@router.get(
    "/{board_id}",
    response_model=ReadBoard,
    summary="Get a board by ID",
    description=(
        "Fetches a single board by its numeric ID.\n\n"
        "Returns 404 if the board does not exist."
    ),
)
def get_board_endpoint(board_id: int, session: Session = Depends(get_session)):
    """
    Get a single board by ID.
    """
    return get_board(id=board_id, session=session)


@router.patch(
    "/{board_id}",
    response_model=ReadBoard,
    summary="Update a board",
    description=(
        "Partially updates a board.\n\n"
        "Currently supports updating the board `name`.\n"
        "Returns 404 if the board does not exist."
    ),
)
def update_board_endpoint(
    board_id: int,
    payload: UpdateBoard,
    session: Session = Depends(get_session),
):
    """
    Update a board.

    Note: `UpdateBoard` includes fields like `updated_at` today, but this endpoint
    only applies the `name` field if provided.
    """
    # UpdateBoard currently includes `name` + `updated_at`; keep API ergonomic by
    # only using `name` if present.
    new_name = getattr(payload, "name", "") or ""
    return update_board(id=board_id, session=session, new_name=new_name)


@router.delete(
    "/{board_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Delete a board",
    description=(
        "Deletes a board by ID.\n\n"
        "Returns 204 No Content on success. Returns 404 if the board does not exist."
    ),
)
def delete_board_endpoint(
    board_id: int, session: Session = Depends(get_session)
) -> Response:
    """
    Delete a board.

    This permanently removes the board record (and may cascade depending on DB constraints).
    """
    delete_board(id=board_id, session=session)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/{board_id}/tasks",
    response_model=List[ReadTask],
    summary="List tasks for a board",
    description=(
        "Returns all tasks that belong to the given board.\n\n"
        "Use this to display the board's task list/lanes in a kanban UI.\n"
        "Returns 404 if the board does not exist."
    ),
)
def get_board_tasks_endpoint(board_id: int, session: Session = Depends(get_session)):
    """
    List tasks for a specific board.
    """
    board = get_board_with_tasks(id=board_id, session=session)
    return list(board.tasks or [])
