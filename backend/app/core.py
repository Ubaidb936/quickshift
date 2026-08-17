import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.authentication import router as auth_router
from app.api.shifts import router as shifts_router
from app.api.matches import router as matches_router
from app.api.agent import router as agent_router
from app.middleware import LoggingMiddleware


def create_app(lifespan=None) -> FastAPI:
    app = FastAPI(title="QuickShift API", version="1.0.0", lifespan=lifespan)

    # ── Suppress uvicorn's built-in access log — our middleware handles it ──
    logging.getLogger("uvicorn.access").handlers.clear()
    logging.getLogger("uvicorn.access").propagate = False

    # ── Middleware (order matters: first added = outermost) ─────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(LoggingMiddleware)

    # ── Routers ─────────────────────────────────────────────────────────────
    app.include_router(auth_router)
    app.include_router(shifts_router)
    app.include_router(matches_router)
    app.include_router(agent_router)

    return app
