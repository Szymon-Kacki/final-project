from sqlalchemy import Integer, String
from app.models import Book, User

def test_book_model_structure():
    assert Book.__tablename__ == "books"

    # require all expected attributes
    for attr in ["id", "title", "author", "description", "year"]:
        assert hasattr(Book, attr)

    # check column types
    assert isinstance(Book.__table__.c.id.type, Integer)
    assert isinstance(Book.__table__.c.title.type, String)
    assert isinstance(Book.__table__.c.author.type, String)
    assert isinstance(Book.__table__.c.description.type, String)
    assert isinstance(Book.__table__.c.year.type, Integer)

def test_user_model_structure():
    assert User.__tablename__ == "users"

    expected_columns = ["id", "username", "hashed_password", "role"]
    
    for attr in expected_columns:
        assert hasattr(User, attr)

    assert isinstance(User.__table__.c.id.type, Integer)
    assert isinstance(User.__table__.c.username.type, String)
    assert isinstance(User.__table__.c.hashed_password.type, String)
    assert isinstance(User.__table__.c.role.type, String)