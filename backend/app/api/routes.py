from fastapi import APIRouter
from app.schemas.start_schema import StartRequest, StartResponse
import uuid
import random

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


@router.post("/start", response_model=StartResponse)
def start_game(payload: StartRequest):
    user_id = str(uuid.uuid4())
    board_size = 3
    flat_tasks = random.sample(TASK_POOL, k=board_size * board_size)

    grid_tasks = [
        flat_tasks[i * board_size:(i + 1) * board_size]
        for i in range(board_size)
    ]

    return StartResponse(
        user_id=user_id,
        name=payload.name,
        board_size=board_size,
        tasks=grid_tasks
    )

