import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.main import app
from app.database import get_db

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

def get_admin_headers():

    login_data = {"username": "test_admin", "password": "password", "role": "admin"}
    
    # 1. Rejestracja (backend wymusza role='user', ale my tutaj zasymulujemy 
    #    admina przez init_db albo stworzenie superusera w inny sposób. 
    #    ALE: Ponieważ w testach używamy pustej bazy SQLite, init_db się nie odpalił automatem.
    #    Musimy stworzyć admina "ręcznie" w bazie lub użyć endpointu jeśli pozwala.
    #    W Twoim kodzie rejestracja wymusza role="user". 
    #    Więc dla testów musimy "oszukać" system i wstrzyknąć admina do bazy."""
    
    client.post("/auth/register", json={"username": "test_admin", "password": "password"})
    
    db = TestingSessionLocal()
    from app.models import User
    user = db.query(User).filter(User.username == "test_admin").first()
    if user:
        user.role = "admin"
        db.commit()
    db.close()

    response = client.post("/auth/login", data={"username": "test_admin", "password": "password"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def get_user_headers():
    login_data = {"username": "test_user_normal", "password": "password"}
    client.post("/auth/register", json=login_data)
    response = client.post("/auth/login", data=login_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_list_books_empty_db():
    response = client.get("/books/")
    assert response.status_code == 200
    assert response.json() == []

def test_create_book():
    admin_headers = get_admin_headers()
    new_book = {
        "title": "Testowa Książka",
        "author": "Testowy Autor",
        "description": "Testowy opis książki.",
        "year": 2026
    }
    response = client.post("/books/", json=new_book, headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == new_book["title"]
    assert data["author"] == new_book["author"]

def test_create_book_optional_fields_none():
    admin_headers = get_admin_headers()
    minimal_book = {"title": "Przykładowa nazwa", "author": "Autor"}
    response = client.post("/books/", json=minimal_book, headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["description"] is None
    assert data["year"] is None

def test_create_book_invalid_missing_field():
    admin_headers = get_admin_headers()
    incomplete_book = {"title": "Tylko tytuł"}  # missing author
    response = client.post("/books/", json=incomplete_book, headers=admin_headers)
    assert response.status_code == 422

def test_create_book_invalid_type():
    admin_headers = get_admin_headers()
    invalid_book = {
        "title": "Tytuł",
        "author": "Autor",
        "description": "Opis książki",
        "year": "Nieprawidłowy rok"
    }
    response = client.post("/books/", json=invalid_book, headers=admin_headers)
    assert response.status_code == 422

def test_update_book():
    admin_headers = get_admin_headers()
    create_resp = client.post("/books/", json={
        "title": "Stary Tytul",
        "author": "Autor",
        "year": 2000,
        "description": "Opis"
    }, headers=admin_headers)

    book_id = create_resp.json()["id"]

    user_headers = get_user_headers()

    update_data = {
        "title": "Nowy Tytul",
        "year": 2025
    }

    response = client.put(f"/books/{book_id}", json=update_data, headers=user_headers)
    
    assert response.status_code == 200
    
    data = response.json()
    assert data["title"] == "Nowy Tytul"
    assert data["year"] == 2025
    assert data["author"] == "Autor"

def test_update_book_unauthorized():

    admin_headers = get_admin_headers()
    create_resp = client.post("/books/", json={
        "title": "Do Zmiany",
        "author": "Autor"
    }, headers=admin_headers)

    book_id = create_resp.json()["id"]
    update_data = {"title": "Zmiana tytułu"}
    
    response = client.put(f"/books/{book_id}", json=update_data)
    assert response.status_code == 401

def test_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.text

def test_delete_book_as_admin():
    admin_headers = get_admin_headers()
    create_resp = client.post("/books/", json={"title": "Do Usuniecia", "author": "X"}, headers=admin_headers)
    book_id = create_resp.json()["id"]

    del_resp = client.delete(f"/books/{book_id}", headers=admin_headers)
    assert del_resp.status_code == 204
    
    get_resp = client.get("/books/")
    books = get_resp.json()

    assert not any(b['id'] == book_id for b in books)

def test_delete_book_as_user_forbidden():
    admin_headers = get_admin_headers()
    create_resp = client.post("/books/", json={"title": "Nie rusz", "author": "X"}, headers=admin_headers)
    book_id = create_resp.json()["id"]

    user_headers = get_user_headers()
    del_resp = client.delete(f"/books/{book_id}", headers=user_headers)
    
    assert del_resp.status_code == 403