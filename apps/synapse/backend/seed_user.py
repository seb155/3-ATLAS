from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.auth import User


def seed_user():
    db = SessionLocal()
    email = "admin@aurumax.com"
    password = "admin123!"

    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"Creating user: {email}")
            hashed_password = get_password_hash(password)
            user = User(email=email, hashed_password=hashed_password, full_name="Admin User")
            db.add(user)
            db.commit()
            print("User created successfully.")
        else:
            print("User already exists.")
    except Exception as e:
        print(f"Error seeding user: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_user()
