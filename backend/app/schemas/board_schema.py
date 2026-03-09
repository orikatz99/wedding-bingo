from pydantic import BaseModel
from typing import Optional


class BingoCell(BaseModel):
    task: str
    completed: bool = False
    image_url: Optional[str] = None
    completed_at: Optional[str] = None
