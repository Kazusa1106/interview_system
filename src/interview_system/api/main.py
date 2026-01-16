"""FastAPI 应用工厂。"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from interview_system.api.exceptions import register_exception_handlers
from interview_system.api.routes import health, interview, session
from interview_system.config import settings as _settings
from interview_system.config.logging import configure_logging
from interview_system.config.settings import Settings
from interview_system.infrastructure.cache.memory_cache import SessionCache
from interview_system.infrastructure.database.connection import AsyncDatabase


def create_app(settings: Settings) -> FastAPI:
    """创建 FastAPI app（允许测试时传入不同 Settings）。"""
    configure_logging(log_level=settings.log_level)

    @asynccontextmanager
    async def lifespan(app: FastAPI):  # noqa: ANN001
        app.state.settings = settings
        app.state.session_cache = SessionCache()
        app.state.db = AsyncDatabase(settings.database_url)
        await app.state.db.init()
        yield
        await app.state.db.dispose()

    app = FastAPI(
        title="Interview System API",
        version="2.0.0",
        description="REST API for AI-powered interview platform",
        lifespan=lifespan,
    )

    register_exception_handlers(app)

    default_origins = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=default_origins + list(settings.allowed_origins),
        allow_origin_regex=r"https://.*\.(trycloudflare\.com|ngrok-free\.app|ngrok\.io)",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(session.router, prefix="/api")
    app.include_router(interview.router, prefix="/api")
    app.include_router(health.router)

    @app.get("/")
    async def root():  # noqa: D401
        return {
            "service": "Interview System API",
            "version": "2.0.0",
            "docs": "/docs",
            "health": "/health",
        }

    return app


app = create_app(_settings)
