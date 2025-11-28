import logging
import time

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

# Configure logging for slow queries
_query_logger = logging.getLogger("synapse.queries")

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Query timing for performance monitoring
@event.listens_for(Engine, "before_cursor_execute")
def _before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Record query start time."""
    conn.info.setdefault("query_start_time", []).append(time.time())


@event.listens_for(Engine, "after_cursor_execute")
def _after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Log slow queries (>500ms)."""
    start_times = conn.info.get("query_start_time", [])
    if start_times:
        total_time = time.time() - start_times.pop(-1)
        # Log queries taking more than 500ms
        if total_time > 0.5:
            _query_logger.warning(
                f"Slow query ({total_time:.2f}s): {statement[:200]}..."
                if len(statement) > 200
                else f"Slow query ({total_time:.2f}s): {statement}"
            )


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
