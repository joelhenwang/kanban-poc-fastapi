from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.task import ReadTask, Task
from app.models.user import CreateUser, ReadUser, UpdateUser, User

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post(
    "",
    response_model=ReadUser,
    status_code=status.HTTP_201_CREATED,
    summary="Create a user",
    description=(
        "Creates a new user record.\n\n"
        "You typically create users first, then reference them from tasks:\n"
        "- as `author_id` (creator of the task)\n"
        "- as `assignee_id` (the single user currently assigned to the task)\n"
    ),
)
def create_user(payload: CreateUser, session: Session = Depends(get_session)) -> User:
    """
    Create a new user.

    Purpose:
    - Provides a stable `user_id` that can be referenced by tasks (author/assignee).
    """
    user = User(name=payload.name)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.get(
    "",
    response_model=List[ReadUser],
    summary="List users",
    description=(
        "Returns a paginated list of users.\n\n"
        "Use this endpoint to:\n"
        "- Browse existing users\n"
        "- Find a user ID to use as `author_id`/`assignee_id` when creating or updating tasks\n"
    ),
)
def list_users(
    q: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    session: Session = Depends(get_session),
) -> List[User]:
    """
    List users.

    Purpose:
    - Lightweight directory of users you can reference from task operations.
    """
    stmt = select(User)
    if q:
        stmt = stmt.where(User.name.contains(q))  # pyright: ignore[reportAttributeAccessIssue]
    stmt = stmt.offset(offset).limit(limit)
    return list(session.exec(stmt).all())


@router.get(
    "/{user_id}",
    response_model=ReadUser,
    summary="Get a user by ID",
    description=(
        "Fetches a single user record by its numeric ID.\n\n"
        "Use this endpoint to:\n"
        "- Validate that a user exists before assigning tasks\n"
        "- Retrieve user details for UI/profile screens\n"
    ),
)
def get_user(user_id: int, session: Session = Depends(get_session)) -> User:
    """
    Get a user by ID.

    Purpose:
    - Lookup endpoint for validating user references (e.g., assignee_id).
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.patch(
    "/{user_id}",
    response_model=ReadUser,
    summary="Update a user",
    description=(
        "Updates mutable fields on the user (currently just `name`).\n\n"
        "Use this endpoint to:\n"
        "- Rename a user\n"
        "- Keep the `updated_at` timestamp current\n"
    ),
)
def update_user(
    user_id: int,
    payload: UpdateUser,
    session: Session = Depends(get_session),
) -> User:
    """
    Update a user.

    Purpose:
    - Allows changing user display/name fields.
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Update fields
    if payload.name:
        user.name = payload.name
    user.updated_at = getattr(payload, "updated_at", None) or datetime.now()

    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Delete a user",
    description=(
        "Deletes a user by ID.\n\n"
        "Returns 204 No Content on success.\n\n"
        "Notes:\n"
        "- If tasks reference this user (as author/assignee), the database may reject deletion\n"
        "  depending on your FK constraints.\n"
        "- Consider 'soft delete' or reassigning tasks before deleting users in real systems.\n"
    ),
)
def delete_user(user_id: int, session: Session = Depends(get_session)) -> Response:
    """
    Delete a user.

    Purpose:
    - Remove a user record (typically admin-only in real applications).
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    session.delete(user)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/{user_id}/tasks/authored",
    response_model=List[ReadTask],
    summary="List tasks authored by a user",
    description=(
        "Returns tasks where the given user is the author/creator.\n\n"
        "Use this endpoint for:\n"
        "- 'Created by me' views\n"
        "- Auditing or reporting on who created work items\n"
    ),
)
def list_user_tasks_authored(
    user_id: int, session: Session = Depends(get_session)
) -> List[Task]:
    """
    List tasks authored by a user.

    Purpose:
    - Power user-centric views like \"Created by me\".
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Ensure relationship is loaded
    _ = user.tasks_authored
    return list(user.tasks_authored)


@router.get(
    "/{user_id}/tasks",
    response_model=Dict[str, List[ReadTask]],
    summary="List tasks for a user (combined)",
    description=(
        "Returns tasks related to the user in a single response, split into two lists:\n\n"
        "- `authored`: tasks where the user is the author/creator\n"
        "- `assigned`: tasks where the user is the current assignee\n\n"
        'Use this endpoint to power a single "User Tasks" screen without making multiple HTTP calls.'
    ),
)
def list_user_tasks_combined(
    user_id: int, session: Session = Depends(get_session)
) -> Dict[str, List[Task]]:
    """
    List tasks for a user in a combined response.

    Purpose:
    - Provide a single endpoint for UI/screens that need both authored and assigned tasks.
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Ensure relationships are loaded
    _ = user.tasks_authored
    _ = user.tasks_assigned

    return {
        "authored": list(user.tasks_authored),
        "assigned": list(user.tasks_assigned),
    }


@router.get(
    "/{user_id}/tasks/assigned",
    response_model=List[ReadTask],
    summary="List tasks assigned to a user",
    description=(
        "Returns tasks where the given user is the current assignee.\n\n"
        "Use this endpoint for:\n"
        "- 'My tasks' / 'Assigned to me' views\n"
        "- Workload and queue screens\n"
    ),
)
def list_user_tasks_assigned(
    user_id: int, session: Session = Depends(get_session)
) -> List[Task]:
    """
    List tasks assigned to a user.

    Purpose:
    - Power user-centric views like \"Assigned to me\" / \"My tasks\".
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Ensure relationship is loaded
    _ = user.tasks_assigned
    return list(user.tasks_assigned)
