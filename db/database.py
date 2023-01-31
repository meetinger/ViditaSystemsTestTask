from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session, scoped_session

from core.settings import settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
engine = create_engine(SQLALCHEMY_DATABASE_URL)

session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

ScopedSession = scoped_session(session_factory)

Base = declarative_base()


@contextmanager
def get_db() -> Session:
    db = None
    try:
        db = ScopedSession()
        yield db
    finally:
        return None
