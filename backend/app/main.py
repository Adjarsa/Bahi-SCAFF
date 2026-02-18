from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.health import router as health_router
from app.api.routes.pipeline import router as pipeline_router
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="API interne facade + echafaudage",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.allow_origin],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health_router, prefix="/api/v1")
    app.include_router(pipeline_router, prefix="/api/v1")

    @app.get("/")
    def root() -> dict[str, str]:
        return {"message": "Bahi-SCAFF API active"}

    return app


app = create_app()
