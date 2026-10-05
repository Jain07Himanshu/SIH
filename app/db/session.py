import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import get_config
from app.db.models import Base

_engine = None
_SessionFactory = None

def get_engine():
    global _engine
    if _engine is None:
        config = get_config()
        db_url = os.environ.get("DATABASE_URL", config.database.url)
        connect_args = {"check_same_thread": False} if db_url.startswith("sqlite") else {}
        _engine = create_engine(db_url, echo=config.database.echo, connect_args=connect_args)
    return _engine

def get_session_factory():
    global _SessionFactory
    if _SessionFactory is None:
        engine = get_engine()
        _SessionFactory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return _SessionFactory

def get_db():
    factory = get_session_factory()
    db = factory()
    try:
        yield db
    finally:
        db.close()

def init_db():
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    print("Database tables initialized successfully.")
