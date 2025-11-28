from app.core.database import SessionLocal
from app.core.security import verify_password
from app.models.auth import User


def verify_user():
    db = SessionLocal()
    email = "goldmine_admin@example.com"
    password = "password"

    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"User {email} not found.")
        else:
            print(f"User found: {user.email}")
            if verify_password(password, user.hashed_password):
                print("Password verification SUCCESS.")
            else:
                print("Password verification FAILED.")
                print(f"Hashed password in DB: {user.hashed_password}")
    except Exception as e:
        print(f"Error verifying user: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verify_user()
