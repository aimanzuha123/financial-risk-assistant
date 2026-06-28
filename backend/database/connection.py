"""
Database Connection Manager
Handles SQLite connection, session lifecycle, and database initialization.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.settings import settings
from .models import Base

engine = create_engine(
    str(settings.DATABASE_URL),
    connect_args={"check_same_thread": False},  # SQLite-specific
    echo=settings.DEBUG,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Create all tables defined in models."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency — yields a database session and ensures cleanup."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
