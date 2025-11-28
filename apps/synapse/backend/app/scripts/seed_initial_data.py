from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.auth import Client, Project, User, UserRole


def seed_initial_data():
    db = SessionLocal()
    try:
        # 1. Create Default User
        user = db.query(User).filter(User.email == "admin@aurumax.com").first()
        if not user:
            print("Creating default user: admin@aurumax.com")
            user = User(
                email="admin@aurumax.com",
                hashed_password=get_password_hash("admin123!"),
                full_name="Admin User",
                role=UserRole.ADMIN,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            print("Default user already exists")

        # 2. Create Default Client
        client = db.query(Client).filter(Client.name == "Mockup Client").first()
        if not client:
            print("Creating default client: Mockup Client")
            client = Client(name="Mockup Client", contact_email="contact@mockup.com")
            db.add(client)
            db.commit()
            db.refresh(client)
        else:
            print("Default client already exists")

        # 3. Create Default Project
        project = db.query(Project).filter(Project.name == "Default Project").first()
        if not project:
            print("Creating default project: Default Project")
            project = Project(
                name="Default Project",
                client_id=client.id,
                description="Default project for testing and development",
                status="ACTIVE",
            )
            db.add(project)
            db.commit()
            db.refresh(project)
        else:
            print("Default project already exists")

    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_initial_data()
