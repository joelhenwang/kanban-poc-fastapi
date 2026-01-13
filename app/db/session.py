import os
from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

# SQLite by default; override with DATABASE_URL env var, e.g.:
# DATABASE_URL=postgresql+psycopg2://neondb_owner:npg_yeTi5N3OKDZg@ep-small-bonus-agqsvojd-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://neondb_owner:npg_yeTi5N3OKDZg@ep-small-bonus-agqsvojd-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require",
)

# Needed for SQLite when using the app in a multi-threaded environment (e.g. Uvicorn).
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    echo=os.getenv("SQL_ECHO", "0") in {"1", "true", "True", "yes", "YES"},
    connect_args=connect_args,
)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
