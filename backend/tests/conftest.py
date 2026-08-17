import os
import pytest
import redis.asyncio as aioredis
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.database.db import Base, get_db
from app.database.redis import redis_client
from main import app

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://quickshift:quickshift@localhost:5432/quickshift_test"
)
# db=1 isolates test data from the dev db=0
TEST_REDIS_URL = os.getenv("TEST_REDIS_URL", "redis://localhost:6379/1")


@pytest.fixture
async def client():
    # create engine and tables fresh for every test
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # each request gets its own session — avoids "operation in progress" errors
    async def override_get_db():
        async with async_session() as session:
            yield session

    test_redis = aioredis.from_url(TEST_REDIS_URL, decode_responses=True)
    redis_client.client = test_redis

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    # teardown — flush test redis db and close
    app.dependency_overrides.clear()
    await test_redis.flushdb()
    close = getattr(test_redis, 'aclose', None) or getattr(test_redis, 'close')
    await close()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()
