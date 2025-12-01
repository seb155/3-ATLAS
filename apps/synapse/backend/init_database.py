#!/usr/bin/env python
"""
Database Initialization Master Script

This script handles the complete database setup:
1. Creates all tables (schema)
2. Seeds initial data (admin user, default client/project)
3. Optionally seeds baseline rules

Usage:
    python init_database.py              # Schema + Initial Data
    python init_database.py --with-rules  # Also seed baseline rules
    python init_database.py --reset       # Drop all and recreate
"""

import argparse
import logging
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import Base, SessionLocal, engine
from app.core.security import get_password_hash
from app.models.auth import Client, Project, User, UserRole

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def drop_all_tables():
    """Drop all existing tables (DESTRUCTIVE)"""
    logger.warning("⚠️  Dropping all tables...")
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("✅ All tables dropped")
    except Exception as e:
        logger.error(f"❌ Error dropping tables: {e}")
        raise


def create_schema():
    """Create all database tables"""
    logger.info("🏗️  Creating database schema...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database schema created successfully")
    except Exception as e:
        logger.error(f"❌ Error creating schema: {e}")
        raise


def seed_initial_data():
    """Seed initial data (admin user, default client/project)"""
    logger.info("🌱 Seeding initial data...")
    db = SessionLocal()
    try:
        # 1. Create Default Admin User
        user = db.query(User).filter(User.email == "admin@aurumax.com").first()
        if not user:
            logger.info("Creating admin user: admin@aurumax.com")
            user = User(
                email="admin@aurumax.com",
                hashed_password=get_password_hash("admin123!"),
                full_name="Admin User",
                role=UserRole.ADMIN,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info("✅ Admin user created")
        else:
            logger.info("ℹ️  Admin user already exists")

        # 2. Create Default Client
        client = db.query(Client).filter(Client.name == "AuruMax Mining").first()
        if not client:
            logger.info("Creating default client: AuruMax Mining")
            client = Client(name="AuruMax Mining", contact_email="contact@aurumax.com")
            db.add(client)
            db.commit()
            db.refresh(client)
            logger.info("✅ Default client created")
        else:
            logger.info("ℹ️  Default client already exists")

        # 3. Create Default Project
        project = db.query(Project).filter(Project.name == "Gold Mine Project").first()
        if not project:
            logger.info("Creating default project: Gold Mine Project")
            project = Project(
                name="Gold Mine Project",
                client_id=client.id,
                description="Default project for testing and development",
                status="ACTIVE",
            )
            db.add(project)
            db.commit()
            db.refresh(project)
            logger.info("✅ Default project created")
        else:
            logger.info("ℹ️  Default project already exists")

        logger.info("✅ Initial data seeding complete")

    except Exception as e:
        logger.error(f"❌ Error seeding data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def seed_baseline_rules():
    """Seed baseline rules (optional)"""
    logger.info("📝 Seeding baseline rules...")
    try:
        from app.scripts.seed_cable_rules import seed_cable_rules

        seed_cable_rules()
        logger.info("✅ Baseline rules seeded")
    except ImportError:
        logger.warning("⚠️  Baseline rules script not found, skipping...")
    except Exception as e:
        logger.error(f"❌ Error seeding rules: {e}")
        raise


def main():
    parser = argparse.ArgumentParser(description="Initialize SYNAPSE database")
    parser.add_argument(
        "--reset", action="store_true", help="Drop all tables and recreate (DESTRUCTIVE)"
    )
    parser.add_argument("--with-rules", action="store_true", help="Also seed baseline rules")
    parser.add_argument(
        "--schema-only", action="store_true", help="Only create schema, skip data seeding"
    )

    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("🚀 SYNAPSE Database Initialization")
    logger.info("=" * 60)

    try:
        # Step 1: Reset if requested
        if args.reset:
            confirm = input("⚠️  This will DELETE ALL DATA. Are you sure? (yes/no): ")
            if confirm.lower() != "yes":
                logger.info("Cancelled.")
                return
            drop_all_tables()

        # Step 2: Create schema
        create_schema()

        # Step 3: Seed data (unless schema-only)
        if not args.schema_only:
            seed_initial_data()

            # Step 4: Seed rules if requested
            if args.with_rules:
                seed_baseline_rules()

        logger.info("=" * 60)
        logger.info("✅ Database initialization complete!")
        logger.info("=" * 60)
        logger.info("Default credentials:")
        logger.info("  Email: admin@aurumax.com")
        logger.info("  Password: admin123!")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"❌ Initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
