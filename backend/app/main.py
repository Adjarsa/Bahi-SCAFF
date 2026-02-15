from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.core.config import get_settings
from app.db.init_db import init_db
from app.db.session import SessionLocal

settings = get_settings()
app = FastAPI(title=settings.app_name, version=settings.app_version)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    Path(settings.storage_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.export_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    db = SessionLocal()
    try:
        init_db(db)
    finally:
        db.close()


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "ScaffoldPlan AI API operationnelle"}


app.include_router(api_router, prefix=settings.api_prefix)
