from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from pathlib import Path
import uuid
import random
import shutil

from app.schemas.board_schema import BingoCell
from app.schemas.start_schema import StartRequest, StartResponse
from app.schemas.complete_task_schema import CompleteTaskRequest
from app.services.bingo_checker import has_bingo
from app.db.session import get_db
from app.db.models import User, Board, BoardTask, Winner

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

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
def start_game(payload: StartRequest, db: Session = Depends(get_db)):
    board_size = 3
    flat_tasks = random.sample(TASK_POOL, k=board_size * board_size)

    cells = [BingoCell(task=t) for t in flat_tasks]

    grid_tasks = [
        cells[i * board_size:(i + 1) * board_size]
        for i in range(board_size)
    ]

    new_user = User(guest_name=payload.name)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    new_board = Board(user_id=new_user.id)
    db.add(new_board)
    db.commit()
    db.refresh(new_board)

    for row_index, row in enumerate(grid_tasks):
        for col_index, cell in enumerate(row):
            new_task = BoardTask(
                board_id=new_board.id,
                task_text=cell.task,
                row=row_index,
                col=col_index,
                is_completed=False,
                image_url=None,
                completed_at=None
            )
            db.add(new_task)

    db.commit()

    return StartResponse(
        user_id=str(new_user.id),
        name=payload.name,
        board_size=board_size,
        tasks=grid_tasks
    )


@router.get("/board/{user_id}")
def get_board(user_id: str, db: Session = Depends(get_db)):
    try:
        user_id_int = int(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user_id")

    user = db.query(User).filter(User.id == user_id_int).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    board = db.query(Board).filter(Board.user_id == user.id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    tasks = (
        db.query(BoardTask)
        .filter(BoardTask.board_id == board.id)
        .all()
    )

    board_size = 3
    grid = [[None for _ in range(board_size)] for _ in range(board_size)]

    for task in tasks:
        grid[task.row][task.col] = {
            "task": task.task_text,
            "completed": task.is_completed,
            "image_url": task.image_url,
            "completed_at": task.completed_at
        }

    return {
        "user_id": user_id,
        "board_size": board_size,
        "tasks": grid
    }


@router.post("/complete-task")
def complete_task(payload: CompleteTaskRequest, db: Session = Depends(get_db)):
    try:
        user_id_int = int(payload.user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user_id")

    user = db.query(User).filter(User.id == user_id_int).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    board = db.query(Board).filter(Board.user_id == user.id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    task = (
        db.query(BoardTask)
        .filter(
            BoardTask.board_id == board.id,
            BoardTask.row == payload.row,
            BoardTask.col == payload.col
        )
        .first()
    )

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.is_completed = True
    task.image_url = payload.image_url
    task.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(task)

    board_tasks = (
        db.query(BoardTask)
        .filter(BoardTask.board_id == board.id)
        .all()
    )

    board_size = 3
    grid = [[None for _ in range(board_size)] for _ in range(board_size)]

    for board_task in board_tasks:
        grid[board_task.row][board_task.col] = BingoCell(
            task=board_task.task_text,
            completed=board_task.is_completed,
            image_url=board_task.image_url,
            completed_at=board_task.completed_at.isoformat() if board_task.completed_at else None
        )

    is_bingo = has_bingo(grid)

    if is_bingo:
        existing_winner = (
            db.query(Winner)
            .filter(Winner.user_id == user.id, Winner.board_id == board.id)
            .first()
        )

        if not existing_winner:
            new_winner = Winner(
                user_id=user.id,
                board_id=board.id,
                bingo_at=datetime.utcnow()
            )
            db.add(new_winner)
            db.commit()

    return {
        "message": "Task marked as completed",
        "user_id": payload.user_id,
        "row": payload.row,
        "col": payload.col,
        "cell": {
            "task": task.task_text,
            "completed": task.is_completed,
            "image_url": task.image_url,
            "completed_at": task.completed_at
        },
        "has_bingo": is_bingo
    }


@router.get("/leaderboard")
def get_leaderboard(db: Session = Depends(get_db)):
    winners = db.query(Winner).order_by(Winner.bingo_at.asc()).all()

    leaders = []

    for winner in winners:
        user = db.query(User).filter(User.id == winner.user_id).first()

        leaders.append({
            "user_id": str(winner.user_id),
            "name": user.guest_name if user else "Unknown",
            "bingo_at": winner.bingo_at
        })

    return {
        "count": len(leaders),
        "leaders": leaders
    }


@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    file_extension = file.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = UPLOAD_DIR / unique_filename

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "filename": unique_filename,
        "url": f"/uploads/{unique_filename}"
    }