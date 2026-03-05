from pydantic import BaseModel, Field
from typing import List
from app.schemas.board_schema import BingoCell


class StartRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)


class StartResponse(BaseModel):
    user_id: str
    name: str
    board_size: int
    tasks: List[List[BingoCell]]


