from fastapi import APIRouter

from app.api.routes import health, scan, topics

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(scan.router, prefix="/scan", tags=["scan"])
api_router.include_router(topics.router, prefix="/topics", tags=["topics"])

