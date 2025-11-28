import logging
import os
import sys

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import Base, engine  # noqa: E402

# Import all models to ensure they are registered with Base

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_schema():
    logger.info("🏗️  Creating database schema...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database schema created successfully!")
    except Exception as e:
        logger.error(f"❌ Error creating schema: {e}")
        raise


if __name__ == "__main__":
    init_schema()
