from collections.abc import Generator

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings


engine: Engine | None = None
SessionLocal: sessionmaker[Session] | None = None


def init_engine(database_url: str | None = None) -> Engine:
    global engine, SessionLocal

    resolved_database_url = database_url or settings.database_url
    connect_args = {"check_same_thread": False} if resolved_database_url.startswith("sqlite") else {}

    engine = create_engine(
        resolved_database_url,
        future=True,
        pool_pre_ping=True,
        connect_args=connect_args,
    )
    SessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        class_=Session,
    )
    return engine


def get_db() -> Generator[Session, None, None]:
    if SessionLocal is None:
        init_engine()

    if SessionLocal is None:
        raise RuntimeError("Database session factory is not initialized.")

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


init_engine()