from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.utils.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=10,       # keep 10 connections open permanently
    max_overflow=20,    # allow 20 extra during traffic spikes (total max = 30)
    pool_pre_ping=True, # test connection before use — handles DB restarts gracefully
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # don't expire attrs after commit — avoids lazy-load errors
)

Base = declarative_base()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
