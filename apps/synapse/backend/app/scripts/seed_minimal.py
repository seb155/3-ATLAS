"""
Minimal Database Seeding Script
================================
Seeds only the minimum data needed for UI:
1. Admin user
2. Two clients
3. Two projects

Run: python -m app.scripts.seed_minimal
"""

from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.auth import Client, Project, User, UserRole


def main():
    db = SessionLocal()

    try:
        print("=" * 60)
        print("SYNAPSE - Minimal Database Seeding")
        print("=" * 60)

        # 1. Create admin user
        print("\n[1/3] Seeding user...")
        user = db.query(User).filter(User.email == "admin@aurumax.com").first()
        if not user:
            user = User(
                email="admin@aurumax.com",
                hashed_password=get_password_hash("admin123!"),
                full_name="Admin User",
                role=UserRole.ADMIN,
            )
            db.add(user)
            db.commit()
            print("  ✓ Created admin user: admin@aurumax.com / admin123!")
        else:
            print("  ✓ Admin user already exists")

        # 2. Create clients
        print("\n[2/3] Seeding clients...")
        goldmine = db.query(Client).filter(Client.name == "Goldmine Corp").first()
        if not goldmine:
            goldmine = Client(name="Goldmine Corp", contact_email="engineering@goldmine.com")
            db.add(goldmine)
            db.commit()
            db.refresh(goldmine)
            print("  ✓ Created client: Goldmine Corp")
        else:
            print("  ✓ Client 'Goldmine Corp' already exists")

        # 3. Create projects
        print("\n[3/3] Seeding projects...")
        demo_project = db.query(Project).filter(Project.name == "Test Project").first()
        if not demo_project:
            demo_project = Project(
                name="Test Project",
                client_id=goldmine.id,
                description="Demo project for testing SYNAPSE features.",
                status="ACTIVE",
            )
            db.add(demo_project)
            db.commit()
            print("  ✓ Created project: Test Project")
        else:
            print("  ✓ Project 'Test Project' already exists")

        print("\n" + "=" * 60)
        print("✓ Seeding complete!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        import traceback

        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
