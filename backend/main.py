import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
import app.models.models  # noqa: F401 — registers models with SQLAlchemy before table creation
from app.core import create_app
from app.database.db import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = create_app(lifespan=lifespan)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
