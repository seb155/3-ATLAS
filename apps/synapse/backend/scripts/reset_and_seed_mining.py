"""
Reset Database and Seed AuruMax Mining Data

This script:
1. Deletes ALL existing clients, projects, users, nodes, edges, and action logs
2. Creates a fresh mining company setup:
   - Client: AuruMax Mining Corporation
   - Project 1: Northern Crusher Plant
   - Project 2: Tailings Management Facility
   - Admin user: admin@aurumax.com
"""

import logging
import os
import sys

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.action_log import ActionLog
from app.models.auth import Client, Project, User, UserRole
from app.models.metamodel import MetamodelEdge, MetamodelNode
from app.models.rules import RuleExecution

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def reset_database(db):
    """Delete all data from all tables"""
    logger.info("🗑️  Deleting all existing data...")

    try:
        # Delete in correct order (respect foreign keys)
        db.query(RuleExecution).delete()
        logger.info("  ✓ Deleted rule executions")

        db.query(ActionLog).delete()
        logger.info("  ✓ Deleted action logs")

        db.query(MetamodelEdge).delete()
        logger.info("  ✓ Deleted metamodel edges")

        db.query(MetamodelNode).delete()
        logger.info("  ✓ Deleted metamodel nodes")

        db.query(Project).delete()
        logger.info("  ✓ Deleted projects")

        db.query(User).delete()
        logger.info("  ✓ Deleted users")

        db.query(Client).delete()
        logger.info("  ✓ Deleted clients")

        db.commit()
        logger.info("✅ Database cleaned successfully!\n")

    except Exception as e:
        logger.error(f"❌ Error during cleanup: {e}")
        db.rollback()
        raise


def seed_mining_data(db):
    """Create AuruMax Mining Corporation with projects and admin user"""
    logger.info("🏭 Creating AuruMax Mining Corporation...")

    try:
        # 1. Create Client
        client = Client(name="AuruMax Mining Corporation", contact_email="contact@aurumax.com")
        db.add(client)
        db.commit()
        db.refresh(client)
        logger.info(f"  ✓ Created client: {client.name} (ID: {client.id})")

        # 2. Create Project 1: Northern Crusher Plant
        project1 = Project(
            name="Northern Crusher Plant",
            client_id=client.id,
            description="Expansion project for the primary ore crushing facility in the Northern mining sector. Includes new conveyor systems, mill upgrades, and process automation.",
            status="ACTIVE",
        )
        db.add(project1)
        db.commit()
        db.refresh(project1)
        logger.info(f"  ✓ Created project: {project1.name} (ID: {project1.id})")

        # 3. Create Project 2: Tailings Management Facility
        project2 = Project(
            name="Tailings Management Facility",
            client_id=client.id,
            description="New tailings storage facility with advanced monitoring systems, environmental controls, and automated water treatment processes.",
            status="ACTIVE",
        )
        db.add(project2)
        db.commit()
        db.refresh(project2)
        logger.info(f"  ✓ Created project: {project2.name} (ID: {project2.id})")

        # 4. Create Admin User
        admin_user = User(
            email="admin@aurumax.com",
            hashed_password=get_password_hash("Admin123!"),
            full_name="AuruMax Administrator",
            role=UserRole.ADMIN,
            is_active=True,
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        logger.info(f"  ✓ Created admin user: {admin_user.email}")

        # 5. Create Engineer User
        engineer_user = User(
            email="engineer@aurumax.com",
            hashed_password=get_password_hash("Engineer123!"),
            full_name="Sarah Chen",
            role=UserRole.ENGINEER,
            is_active=True,
        )
        db.add(engineer_user)
        db.commit()
        db.refresh(engineer_user)
        logger.info(f"  ✓ Created engineer user: {engineer_user.email}")

        logger.info("\n✅ AuruMax Mining setup completed successfully!")
        logger.info("\n📋 Login Credentials:")
        logger.info("   Admin:    admin@aurumax.com / Admin123!")
        logger.info("   Engineer: engineer@aurumax.com / Engineer123!")
        logger.info("\n📁 Projects:")
        logger.info(f"   1. {project1.name} (ID: {project1.id})")
        logger.info(f"   2. {project2.name} (ID: {project2.id})")

    except Exception as e:
        logger.error(f"❌ Error during seeding: {e}")
        db.rollback()
        raise


def main():
    db = SessionLocal()
    try:
        logger.info("=" * 60)
        logger.info("🔄 RESET AND SEED: AuruMax Mining Corporation")
        logger.info("=" * 60 + "\n")

        # Step 1: Reset
        reset_database(db)

        # Step 2: Seed
        seed_mining_data(db)

        logger.info("\n" + "=" * 60)
        logger.info("✅ ALL DONE! Database is ready for use.")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"\n❌ Fatal error: {e}")
        return 1
    finally:
        db.close()

    return 0


if __name__ == "__main__":
    exit(main())
