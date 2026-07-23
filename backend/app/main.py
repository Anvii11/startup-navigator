from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.db.session import SessionLocal, engine
from app.db.base_models import Base
from app.services.auth import AuthService


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)


def seed_admin() -> None:
    settings = get_settings()
    db = SessionLocal()
    try:
        AuthService.ensure_admin_user(
            db,
            email=settings.admin_email,
            password=settings.admin_password,
            full_name="Platform Admin",
        )
    finally:
        db.close()


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_tables()
    seed_admin()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="Startup Navigator API — Startup Ideas Platform",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_origin_regex=settings.cors_origin_regex,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health", tags=["health"])
    def root_health() -> dict:
        return {
            "status": "ok",
            "app": settings.app_name,
            "env": settings.app_env,
        }

    app.include_router(api_router, prefix="/api/v1")
    return app


app = create_app()
