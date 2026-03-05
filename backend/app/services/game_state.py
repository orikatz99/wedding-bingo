from typing import Dict, List
from app.schemas.board_schema import BingoCell

# In-memory storage for game state
# user_id -> board (3x3)
boards: Dict[str, List[List[BingoCell]]] = {}
