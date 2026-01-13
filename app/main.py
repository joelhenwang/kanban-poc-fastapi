from fastapi import FastAPI

from app.api import board as board_api
from app.api import task as task_api
from app.api import user as user_api
from app.db.session import create_db_and_tables

app = FastAPI(title="Kanban WIP", debug=True)


@app.on_event("startup")
def on_startup() -> None:
    create_db_and_tables()


# API routers
app.include_router(board_api.router)
app.include_router(task_api.router)
app.include_router(user_api.router)
