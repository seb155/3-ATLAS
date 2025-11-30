"""
Database configuration and session management.

Uses FORGE PostgreSQL (shared infrastructure).
"""

from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from .config import get_settings

settings = get_settings()

# =============================================================================
# DATABASE ENGINE
# =============================================================================

engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# =============================================================================
# DEPENDENCIES
# =============================================================================

def get_db() -> Generator[Session, None, None]:
    """
    Dependency for database session.

    Usage:
        from fastapi import Depends

        @app.get("/recordings")
        def get_recordings(db: Session = Depends(get_db)):
            return db.query(Recording).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =============================================================================
# UTILITIES
# =============================================================================

def init_db():
    """
    Initialize database tables.
    Called on application startup.

    Note: In production, use Alembic migrations instead.
    """
    Base.metadata.create_all(bind=engine)


def check_db_connection() -> bool:
    """
    Check if database connection is working.
    Useful for health checks.

    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False
