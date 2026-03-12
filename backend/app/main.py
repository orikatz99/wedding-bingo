from fastapi import FastAPI
from app.api.routes import router
from app.db import database

app = FastAPI(title="Wedding Bingo API")

app.include_router(router)
