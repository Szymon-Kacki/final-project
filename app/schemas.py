from pydantic import BaseModel


class BookBase(BaseModel):
    title: str
    author: str
    description: str | None = None
    year: int | None = None


class BookCreate(BookBase):
    pass


class Book(BookBase):
    id: int

    class Config:
        orm_mode = True

class BookUpdate(BaseModel):
    title: str | None = None
    author: str | None = None
    description: str | None = None
    year: int | None = None

class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str