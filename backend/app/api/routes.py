from fastapi import APIRouter
from app.schemas.board_schema import BingoCell
from app.schemas.start_schema import StartRequest, StartResponse
from app.schemas.complete_task_schema import CompleteTaskRequest
from app.services.bingo_checker import has_bingo
import uuid
import random
from app.services.game_state import boards
from fastapi import HTTPException
from datetime import datetime

router = APIRouter()

# משימות לדוגמה (אחר כך זה יבוא מה-DB)
TASK_POOL = [
    "תרים צ׳ייסר עם החתן/כלה",
    "תעשה סלפי עם מישהו שלא הכרת לפני",
    "תרקוד 30 שניות ברחבה",
    "תצלם את הקינוח שלך",
    "תעשה ברכה קצרה לזוג",
    "תשיר שורה משיר חתונות",
    "תעשה צילום קבוצתי בשולחן שלך",
    "תרים כוסית עם אחד ההורים",
    "תמצא מישהו עם אותו צבע חולצה כמו שלך",
    "תעשה בומרנג ברחבה",
]

@router.get("/")
def root():
    return {"message": "Wedding Bingo API is running"}

@router.get("/health")
def health():
    return {"status": "ok"}

# Endpoint to start a new game
@router.post("/start", response_model=StartResponse)
def start_game(payload: StartRequest):
    user_id = str(uuid.uuid4())
    board_size = 3
    flat_tasks = random.sample(TASK_POOL, k=board_size * board_size)

    cells = [BingoCell(task=t) for t in flat_tasks]

    grid_tasks = [
        cells[i * board_size:(i + 1) * board_size]
        for i in range(board_size)
    ]

    boards[user_id] = grid_tasks

    return StartResponse(
        user_id=user_id,
        name=payload.name,
        board_size=board_size,
        tasks=grid_tasks
    )

# Endpoint to get the current board state
@router.get("/board/{user_id}")
def get_board(user_id: str):
    if user_id not in boards:
        raise HTTPException(status_code=404, detail="Board not found")

    return {
        "user_id": user_id,
        "board_size": 3,
        "tasks": boards[user_id]
    }

# Endpoint to complete a task
@router.post("/complete-task")
def complete_task(payload: CompleteTaskRequest):
    if payload.user_id not in boards:
        raise HTTPException(status_code=404, detail="Board not found")

    board = boards[payload.user_id]
    cell = board[payload.row][payload.col]

    cell.completed = True
    cell.image_url = payload.image_url
    cell.completed_at = datetime.utcnow().isoformat()

    is_bingo = has_bingo(board)

    return {
    "message": "Task marked as completed",
    "user_id": payload.user_id,
    "row": payload.row,
    "col": payload.col,
    "cell": cell,
    "has_bingo": is_bingo
}

