"""SQLite session + table bootstrap.

The compliance DB is intentionally separate from any application DB. The Act
treats the audit log as a regulated artefact distinct from operational data,
and keeping them in different stores makes the boundary obvious.
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings, db_path


Base = declarative_base()

_engine = create_engine(
    f"sqlite:///{db_path()}",
    connect_args={"check_same_thread": False},
)


@event.listens_for(_engine, "connect")
def _enable_sqlite_features(dbapi_conn, _record):
    """Enable WAL + foreign keys. WAL gives us append-mostly behaviour for the
    audit log without blocking readers."""
    cur = dbapi_conn.cursor()
    cur.execute("PRAGMA journal_mode=WAL;")
    cur.execute("PRAGMA foreign_keys=ON;")
    cur.close()


SessionLocal = sessionmaker(bind=_engine, autocommit=False, autoflush=False)


def get_session():
    """FastAPI dependency: yield a session, ensure it's closed."""
    s = SessionLocal()
    try:
        yield s
    finally:
        s.close()


def init_db() -> None:
    """Create tables on first boot. Idempotent."""
    # Import models to register them with the declarative Base.
    from app import models  # noqa: F401
    Base.metadata.create_all(bind=_engine)
