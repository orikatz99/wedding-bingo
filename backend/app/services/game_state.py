from typing import Dict, List
from app.schemas.board_schema import BingoCell

# In-memory storage for game state
# user_id -> board (3x3)
boards: Dict[str, List[List[BingoCell]]] = {}

# user_id -> user name
users: Dict[str, str] = {}

# In-memory storage for winners
# user_id -> winner info 
winners: Dict[str, dict] = {}
