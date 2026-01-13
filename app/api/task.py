from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, Query, Response
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.task import CreateTask, ReadTask, Status, Task, UpdateTask
from app.routers import task as task_service

router = APIRouter(prefix="/tasks", tags=["tasks"])

# -----------------------------------------------------------------------------
# Task API Router
#
# This router exposes CRUD endpoints for `Task` resources.
#
# Concepts:
# - A task can optionally belong to a board (via `board_id`).
# - A task can optionally have an author/creator (via `author_id`).
# - A task can optionally have a single assignee (via `assignee_id`).
# - Task status is one of: todo, in_progress, done.
# -----------------------------------------------------------------------------


@router.post(
    "",
    response_model=ReadTask,
    summary="Create a new task",
    description=(
        "Creates a new task.\n\n"
        "Notes:\n"
        "- `board_id` (optional) associates this task to a board.\n"
        "- `author_id` (optional) indicates who created the task.\n"
        "- `assignee_id` (optional) sets the single assignee for the task.\n"
        "- The returned payload includes generated fields like `id` and timestamps."
    ),
)
def create_task(
    payload: CreateTask,
    session: Session = Depends(get_session),
):
    """
    Create a new task record.

    Purpose:
    - Insert a new task into the database.

    Typical use:
    - Add a task to a board (by providing `board_id`).
    - Track task author (`author_id`) and optional assignee (`assignee_id`).
    """
    task = task_service.create_task(
        name=payload.name,
        description=payload.description,
        status_=payload.status,
        board_id=getattr(payload, "board_id", None),
        author_id=getattr(payload, "author_id", None),
        assignee_id=getattr(payload, "assignee_id", None),
        session=session,
    )

    session.refresh(task)
    return task


@router.get(
    "",
    response_model=List[ReadTask],
    summary="List tasks",
    description=(
        "Returns tasks, optionally filtered by board, author, assignee, or status.\n\n"
        "Query parameters:\n"
        "- `board_id`: Only tasks belonging to the given board\n"
        "- `author_id`: Only tasks created by the given user\n"
        "- `assignee_id`: Only tasks assigned to the given user\n"
        "- `status`: Only tasks matching a status (todo, in_progress, done)"
    ),
)
def list_tasks(
    board_id: Optional[int] = Query(default=None),
    author_id: Optional[int] = Query(default=None),
    assignee_id: Optional[int] = Query(default=None),
    status_: Optional[Status] = Query(default=None, alias="status"),
    session: Session = Depends(get_session),
):
    """
    List tasks with optional filters.

    Purpose:
    - Provide a collection endpoint for tasks.
    - Support basic filtering for common UI needs (board, author, status).
    """
    query = select(Task)

    if board_id is not None:
        query = query.where(Task.board_id == board_id)
    if author_id is not None:
        query = query.where(Task.author_id == author_id)
    if assignee_id is not None:
        query = query.where(Task.assignee_id == assignee_id)
    if status_ is not None:
        query = query.where(Task.status == status_)

    return list(session.exec(query).all())


@router.get(
    "/{task_id}",
    response_model=ReadTask,
    summary="Get a task by id",
    description="Fetch a single task by its integer id. Returns 404 if not found.",
)
def get_task(task_id: int, session: Session = Depends(get_session)):
    """
    Get one task.

    Purpose:
    - Retrieve task details for a task detail view or edit form.
    """
    return task_service.get_task(task_id, session)


@router.patch(
    "/{task_id}",
    response_model=ReadTask,
    summary="Update a task",
    description=(
        "Partially updates a task.\n\n"
        "Typical fields:\n"
        "- `name`, `description`, `status`\n"
        "- `board_id` to move the task to another board (or detach if allowed)\n"
        "- `assignee_id` to assign/unassign a single user"
    ),
)
def update_task(
    task_id: int,
    payload: UpdateTask,
    session: Session = Depends(get_session),
):
    """
    Update a task.

    Purpose:
    - Edit task metadata (name/description/status).
    - Reassign or unassign the task's single assignee.
    - Move the task to another board by changing `board_id`.
    """
    task = task_service.update_task(
        id=task_id,
        session=session,
        new_name=getattr(payload, "name", "") or "",
        new_description=getattr(payload, "description", "") or "",
        new_status=getattr(payload, "status", None),
        new_board_id=getattr(payload, "board_id", None),
        new_author_id=None,
        new_assignee_id=getattr(payload, "assignee_id", None),
    )
    return task


@router.delete(
    "/{task_id}",
    status_code=204,
    response_class=Response,
    summary="Delete a task",
    description="Deletes a task by id. Returns 204 on success, 404 if the task does not exist.",
)
def delete_task(task_id: int, session: Session = Depends(get_session)) -> Response:
    """
    Delete a task.

    Purpose:
    - Remove a task permanently from the system (administrative or cleanup action).
    """
    task_service.delete_task(task_id, session)
    return Response(status_code=204)


@router.get(
    "/{task_id}/author",
    response_model=ReadTask,
    summary="Get a task with its author relationship loaded",
    description=(
        "Fetches a task by id and ensures the `author` relationship is loaded.\n\n"
        "This is useful when you want to return the author information alongside the task."
    ),
)
def get_task_with_author(task_id: int, session: Session = Depends(get_session)):
    """
    Get a task and force-load the author relationship.

    Purpose:
    - Ensure `task.author` is available for serialization/use immediately.
    """
    return task_service.get_task_with_author(task_id, session)


@router.get(
    "/{task_id}/board",
    response_model=ReadTask,
    summary="Get a task with its board relationship loaded",
    description=(
        "Fetches a task by id and ensures the `board` relationship is loaded.\n\n"
        "This is useful when you want to return the board information alongside the task."
    ),
)
def get_task_with_board(task_id: int, session: Session = Depends(get_session)):
    """
    Get a task and force-load the board relationship.

    Purpose:
    - Ensure `task.board` is available for serialization/use immediately.
    """
    return task_service.get_task_with_board(task_id, session)
