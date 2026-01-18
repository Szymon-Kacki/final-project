import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.main import app
from app.routers.books import get_db

# use a temporary SQLite file DB
TEST_DATABASE_URL = "sqlite:///./test_temp.db"  # file-based SQLite
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# override get_db dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# fixture to create tables before tests and drop after
@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)  # create tables
    yield
    Base.metadata.drop_all(bind=engine)    # drop tables
    engine.dispose()                        # close all connections
    if os.path.exists("./test_temp.db"):
        os.remove("./test_temp.db")

client = TestClient(app)


def test_list_books_empty_db():
    response = client.get("/books/")
    assert response.status_code == 200
    assert response.json() == []

def test_create_book():
    new_book = {
        "title": "Testowa Książka",
        "author": "Testowy Autor",
        "description": "Testowy opis książki.",
        "year": 2026
    }
    response = client.post("/books/", json=new_book)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == new_book["title"]
    assert data["author"] == new_book["author"]

def test_create_book_optional_fields_none():
    minimal_book = {"title": "Przykładowa nazwa", "author": "Autor"}
    response = client.post("/books/", json=minimal_book)
    assert response.status_code == 200
    data = response.json()
    assert data["description"] is None
    assert data["year"] is None

def test_create_book_invalid_missing_field():
    incomplete_book = {"title": "Tylko tytuł"}  # missing author
    response = client.post("/books/", json=incomplete_book)
    assert response.status_code == 422

def test_create_book_invalid_type():
    invalid_book = {
        "title": "Tytuł",
        "author": "Autor",
        "description": "Opis książki",
        "year": "Nieprawidłowy rok"
    }
    response = client.post("/books/", json=invalid_book)
    assert response.status_code == 422

def test_update_book():
    create_resp = client.post("/books/", json={
        "title": "Stary Tytul",
        "author": "Autor",
        "year": 2000,
        "description": "Opis"
    })

    book_id = create_resp.json()["id"]

    update_data = {
        "title": "Nowy Tytul",
        "year": 2025
    }
    response = client.put(f"/books/{book_id}", json=update_data)
    
    assert response.status_code == 200
    
    data = response.json()
    assert data["title"] == "Nowy Tytul"
    assert data["year"] == 2025
    assert data["author"] == "Autor"

def test_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.text