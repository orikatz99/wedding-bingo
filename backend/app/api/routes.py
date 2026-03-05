from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def root():
    return {"message": "Wedding Bingo API is running"}

@router.get("/health")
def health():
    return {"status": "ok"}
