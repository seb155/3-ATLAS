"""
Database configuration and session management.

Dual Database Architecture:
1. Main Database (nexus): Application-specific data (notes, tags, etc.)
2. Auth Database (workspace_auth): Shared authentication across workspace apps

This allows Nexus to:
- Store its own data in the 'nexus' database
- Share users with Synapse and other apps via workspace_auth schema
- Support SSO-like authentication across the workspace
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from .config import get_settings

settings = get_settings()

# ============================================================================
# MAIN APPLICATION DATABASE (Nexus)
# ============================================================================

engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,   # Recycle connections every hour
    pool_size=10,        # Connection pool size
    max_overflow=20,     # Max connections beyond pool_size
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for main application database.

    Usage:
        from fastapi import Depends

        @app.get("/notes")
        def get_notes(db: Session = Depends(get_db)):
            return db.query(Note).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================================
# AUTH DATABASE (Workspace Auth Schema)
# ============================================================================

# Create separate engine for workspace_auth schema
auth_engine = create_engine(
    settings.effective_auth_database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=5,        # Smaller pool for auth database
    max_overflow=10,
    # Set search_path to workspace_auth schema if using separate schema
    connect_args={
        "options": "-c search_path=workspace_auth,public"
    } if settings.auth_database_url else {}
)

AuthSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=auth_engine)

AuthBase = declarative_base()


def get_auth_db() -> Generator[Session, None, None]:
    """
    Dependency for shared authentication database.

    Usage:
        from fastapi import Depends

        @app.post("/auth/login")
        def login(db: Session = Depends(get_auth_db)):
            user = db.query(User).filter(User.email == email).first()
            ...
    """
    db = AuthSessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def init_db():
    """
    Initialize database tables.
    Called on application startup.

    Note: In production, use Alembic migrations instead.
    """
    Base.metadata.create_all(bind=engine)
    # Don't create auth tables here - they're managed by workspace init scripts


def check_db_connection():
    """
    Check if database connection is working.
    Useful for health checks.

    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False


def check_auth_db_connection():
    """
    Check if auth database connection is working.

    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        db = AuthSessionLocal()
        db.execute("SELECT 1")
        db.close()
        return True
    except Exception as e:
        print(f"Auth database connection failed: {e}")
        return False
