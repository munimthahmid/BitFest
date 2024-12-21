from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db

router = APIRouter()

@router.get("/hello", tags=["Hello"])
async def hello(db: Session = Depends(get_db)):
    # Example uses database session, but it's not yet doing anything with it
    return {"message": "Hello, World!"}
