from app.core.security import hash_password
from app.db.database import Base, SessionLocal, engine
from app.models.user import User


EMAIL = "analyst@example.com"
PASSWORD = "Demo12345"


Base.metadata.create_all(bind=engine)  # Create the database tables if needed.

db = SessionLocal()
try:
    user = db.query(User).filter(User.email == EMAIL).first()
    if user is not None:
        print(f"Test user already exists: {EMAIL}")
    else:
        db.add(User(email=EMAIL, password_hash=hash_password(PASSWORD)))
        db.commit()
        print(f"Created test user: {EMAIL}")
finally:
    db.close()
