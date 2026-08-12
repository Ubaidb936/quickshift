import uvicorn
import app.models.models  # noqa: F401 — registers models with SQLAlchemy before table creation
from app.core import create_app
from app.database.db import Base, engine

Base.metadata.create_all(bind=engine)

app = create_app()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
