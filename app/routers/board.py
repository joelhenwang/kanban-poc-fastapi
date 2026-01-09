from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, update

from app.models.board import Board


def create_board(name: str, session: Session):
    board = Board(name=name)
    session.add(board)
    session.commit()

    return board


def get_board(id: int, session: Session):
    query = select(Board).where(Board.id == id)
    board = session.exec(query).one()
    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Board not found"
        )
    return board


def update_board(
    id: int, session: Session, new_name: str = "", new_description: str = ""
):
    query = select(Board).where(Board.id == id)
    board = session.exec(query).one()
    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Board not found"
        )

    if new_name:
        board.name = new_name
    if new_description:
        board.description = new_description
    session.add(board)
    session.commit()
    session.refresh(board)

    return board


def delete_board(id: int, session: Session):
    query = select(Board).where(Board.id == id)
    board = session.exec(query).one()
    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Board not found"
        )
    session.delete(board)
    session.commit()


def get_board_with_tasks(id: int, session: Session):
    query = select(Board).where(Board.id == id)
    board = session.exec(query).one()
    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Board not found"
        )

    _ = board.tasks
    return board
