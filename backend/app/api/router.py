from fastapi import APIRouter

from app.api.routers.dashboard import router as dashboard_router
from app.api.routers.exports import router as exports_router
from app.api.routers.generation import router as generation_router
from app.api.routers.health import router as health_router
from app.api.routers.materials import router as materials_router
from app.api.routers.projects import router as projects_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(projects_router)
api_router.include_router(materials_router)
api_router.include_router(generation_router)
api_router.include_router(dashboard_router)
api_router.include_router(exports_router)
