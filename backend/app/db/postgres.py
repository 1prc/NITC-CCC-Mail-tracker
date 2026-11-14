"""PostgreSQL engine and SQLAlchemy session lifecycle."""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from contextlib import contextmanager

from app.core.config import get_settings

_engine = None
_sessions = None


def initialize_database():
    global _engine, _sessions
    url = get_settings().database_url
    if not url:
        return
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    _engine = create_engine(url, pool_pre_ping=True, pool_size=3, max_overflow=2,
                            connect_args={"connect_timeout": 3})
    _sessions = sessionmaker(bind=_engine, autoflush=False, expire_on_commit=False)


def dispose_database():
    global _engine, _sessions
    if _engine:
        _engine.dispose()
    _engine = None
    _sessions = None


def get_session() -> Session:
    if _sessions is None:
        raise RuntimeError("PostgreSQL is not configured. Set DATABASE_URL in backend/.env.")
    session = _sessions()
    try:
        yield session
    finally:
        session.close()


@contextmanager
def session_scope():
    if _sessions is None:
        raise RuntimeError("PostgreSQL is not configured. Set DATABASE_URL in backend/.env.")
    session = _sessions()
    try:
        yield session
    finally:
        session.close()


def create_schema():
    if _engine is None:
        raise RuntimeError("DATABASE_URL is required to create the database schema")
    from app.db.models import Base
    Base.metadata.create_all(_engine)
