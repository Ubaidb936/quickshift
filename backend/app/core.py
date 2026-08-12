from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.authentication import router as auth_router
from app.api.shifts import router as shifts_router
from app.api.matches import router as matches_router


def create_app() -> FastAPI:
    app = FastAPI(title="Instawork Clone", version="1.0.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth_router)
    app.include_router(shifts_router)
    app.include_router(matches_router)

    return app
