from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models.user import User


def create_user(name: str, session: Session):
    user = User(name=name)
    session.add(user)
    session.commit()

    return user


def get_user(id: int, session: Session):
    query = select(User).where(User.id == id)
    user = session.exec(query).one()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


def update_user(id: int, session: Session, new_name: str = ""):
    query = select(User).where(User.id == id)
    user = session.exec(query).one()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if new_name:
        user.name = new_name

    session.add(user)
    session.commit()
    session.refresh(user)

    return user


def delete_user(id: int, session: Session):
    query = select(User).where(User.id == id)
    user = session.exec(query).one()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    session.delete(user)
    session.commit()


def get_user_with_authored_tasks(id: int, session: Session):
    query = select(User).where(User.id == id)
    user = session.exec(query).one()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    _ = user.tasks_authored
    return user


def get_user_with_assigned_tasks(id: int, session: Session):
    query = select(User).where(User.id == id)
    user = session.exec(query).one()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    _ = user.tasks_assigned
    return user
