from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import SessionLocal

router = APIRouter(prefix="/books")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def list_books(db: Session = Depends(get_db)):
    return db.query(models.Book).all()


@router.post("/", response_model=schemas.Book)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    obj = models.Book(title=book.title)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj
