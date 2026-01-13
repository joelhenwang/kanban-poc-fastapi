import os
import tempfile
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from app.db.session import get_session
from app.main import app


@pytest.fixture
def sqlite_db_path(tmp_path: pytest.TempPathFactory) -> str:
    """
    Returns a filesystem path to a temporary SQLite database file.

    Why a file (instead of in-memory SQLite)?
    - It behaves more like a real DB in tests.
    - Multiple connections can see the same data (important for some ORM patterns).
    """
    # pytest provides an isolated temp directory per test run; this file will not be committed
    # and is ignored by `.gitignore`.
    return str(tmp_path / "test.sqlite3")


@pytest.fixture
def engine(sqlite_db_path: str):
    """
    Creates a SQLModel engine bound to a temporary SQLite database file.
    """
    engine = create_engine(
        f"sqlite:///{sqlite_db_path}",
        connect_args={"check_same_thread": False},
    )
    return engine


@pytest.fixture
def session(engine) -> Generator[Session, None, None]:
    """
    Provides a SQLModel session for tests and ensures the schema exists.

    Note:
    - We create tables once per test to keep isolation simple.
    - If you want faster tests later, you can create tables once per session
      and use transactions/rollbacks per test.
    """
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture
def client(engine) -> Generator[TestClient, None, None]:
    """
    FastAPI TestClient with dependency overrides.

    We override `get_session` so API endpoints use the test SQLite DB instead of Neon/other.
    """

    def override_get_session() -> Generator[Session, None, None]:
        SQLModel.metadata.create_all(engine)
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    try:
        with TestClient(app) as c:
            yield c
    finally:
        app.dependency_overrides.clear()
