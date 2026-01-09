from fastapi import FastAPI
from app.routers import board

app = FastAPI(
    title="Kanban WIP"
    debug=True
)


