from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

from collections.abc import Generator
from sqlalchemy.orm import Session


def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency.
    Creates a new SQLAlchemy session for each request
    and closes it automatically.
    """

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()