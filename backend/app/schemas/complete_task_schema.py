from pydantic import BaseModel, Field


class CompleteTaskRequest(BaseModel):
    user_id: str
    row: int = Field(..., ge=0, le=2)
    col: int = Field(..., ge=0, le=2)
    image_url: str
