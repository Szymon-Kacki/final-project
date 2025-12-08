from fastapi import FastAPI, Request
from pathlib import Path
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from routers import books
from database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="LibraryLite")

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(books.router)


@app.on_event("startup")
async def startup_event():
    from app.init_db import init_db
    init_db()


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)