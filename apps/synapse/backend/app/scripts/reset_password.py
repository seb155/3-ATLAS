from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.auth import User


def reset_password():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "admin@aurumax.com").first()
        if user:
            print(f"Resetting password for {user.email}")
            user.hashed_password = get_password_hash("admin123!")
            db.commit()
            print("Password reset successful")
        else:
            print("User not found")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    reset_password()
