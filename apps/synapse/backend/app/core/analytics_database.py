from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Dedicated engine/session for read-only analytics (synapse_analytics.owner.*)
analytics_engine = create_engine(settings.ANALYTICS_SQLALCHEMY_DATABASE_URI)
AnalyticsSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=analytics_engine)


def get_analytics_db():
    db = AnalyticsSessionLocal()
    try:
        yield db
    finally:
        db.close()
