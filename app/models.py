from sqlalchemy import Column, Integer, String
from .database import Base


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    author = Column(String(200), nullable=False)
    description = Column(String(500), nullable=True)
    year = Column(Integer, nullable=True)