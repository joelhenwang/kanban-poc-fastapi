from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models.task import Status, Task


def create_task(
    name: str,
    session: Session,
    description: str = "",
    status_: Status = Status.TODO,
    author_id: int | None = None,
    board_id: int | None = None,
    assignee_id: int | None = None,
):
    task = Task(
        name=name,
        description=description,
        status=status_,
        author_id=author_id,
        board_id=board_id,
        assignee_id=assignee_id,
    )
    session.add(task)
    session.commit()

    return task


def get_task(id: int, session: Session):
    query = select(Task).where(Task.id == id)
    task = session.exec(query).one()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    return task


def get_tasks_by_author(author_id: int, session: Session):
    query = select(Task).where(Task.author_id == author_id)
    tasks = session.exec(query).all()
    if not tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tasks not found"
        )
    return tasks


def get_tasks_by_assignee(assignee_id: int, session: Session):
    query = select(Task).where(Task.assignee_id == assignee_id)
    tasks = session.exec(query).all()
    if not tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tasks not found"
        )
    return tasks


def get_tasks_by_board(board_id: int, session: Session):
    query = select(Task).where(Task.board_id == board_id)
    tasks = session.exec(query).all()
    if not tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tasks not found"
        )
    return tasks


def update_task(
    id: int,
    session: Session,
    new_name: str = "",
    new_description: str = "",
    new_status: Status | None = None,
    new_author_id: int | None = None,
    new_assignee_id: int | None = None,
    new_board_id: int | None = None,
):
    query = select(Task).where(Task.id == id)
    task = session.exec(query).one()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    if new_name:
        task.name = new_name
    if new_description:
        task.description = new_description
    if new_status is not None:
        task.status = new_status
    if new_author_id is not None:
        task.author_id = new_author_id
    if new_assignee_id is not None:
        task.assignee_id = new_assignee_id
    if new_board_id is not None:
        task.board_id = new_board_id

    session.add(task)
    session.commit()
    session.refresh(task)

    return task


def delete_task(id: int, session: Session):
    query = select(Task).where(Task.id == id)
    task = session.exec(query).one()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    session.delete(task)
    session.commit()


def get_task_with_author(id: int, session: Session):
    query = select(Task).where(Task.id == id)
    task = session.exec(query).one()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    _ = task.author
    return task


def get_task_with_board(id: int, session: Session):
    query = select(Task).where(Task.id == id)
    task = session.exec(query).one()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    _ = task.board
    return task
