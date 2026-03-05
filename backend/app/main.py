from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title="Wedding Bingo API")

app.include_router(router)
