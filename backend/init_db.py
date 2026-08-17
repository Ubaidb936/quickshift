"""
Run once before gunicorn starts to create all tables.
Called from docker-compose command before forking workers.
"""
import asyncio
import app.models.models  # noqa — registers models with SQLAlchemy
from app.database.db import Base, engine


async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()


asyncio.run(main())
