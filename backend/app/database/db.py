from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.utils.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    # Connection pool — reuse connections instead of opening a new one per request
    pool_size=10,        # keep 10 connections open permanently
    max_overflow=20,     # allow 20 extra during traffic spikes (total max = 30)
    pool_pre_ping=True,  # test connection before use — handles DB restarts gracefully
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
