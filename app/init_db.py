from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models
from app.auth import get_password_hash

def init_db():
    models.Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()

    if db.query(models.Book).count() == 0:
        sample_books = [
            models.Book(
                title="The Pragmatic Programmer",
                author="Andrew Hunt, David Thomas",
                year=1999,
                description="A classic book about software craftsmanship."
            ),
            models.Book(
                title="Clean Code",
                author="Robert C. Martin",
                year=2008,
                description="A handbook of agile software craftsmanship."
            ),
            models.Book(
                title="Design Patterns: Elements of Reusable OO Software",
                author="Gamma, Helm, Johnson, Vlissides",
                year=1994,
                description="The famous Gang of Four design patterns book."
            ),
        ]

        db.add_all(sample_books)
        db.commit()
        print("Sample books inserted.")
    else:
        print("Books already exist — skipping initialization.")

    admin_user = db.query(models.User).filter(models.User.username == "admin").first()
    
    if not admin_user:
        print("Creating superuser 'admin'...")
        hashed_pwd = get_password_hash("admin")
        
        db_admin = models.User(
            username="admin", 
            hashed_password=hashed_pwd, 
            role="admin" 
        )

        db.add(db_admin)
        db.commit()
        print("Superuser created. Login: admin / Pass: admin123")
    else:
        print("Admin user already exists.")

    db.close()


if __name__ == "__main__":
    init_db()
