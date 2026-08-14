"""API v1 router — aggregates all v1 endpoint routers."""
from fastapi import APIRouter

from app.api.v1.endpoints.jobs import router as jobs_router
from app.api.v1.endpoints.health import router as health_router

router = APIRouter(prefix="/api/v1")
router.include_router(health_router, tags=["Health"])
router.include_router(jobs_router, prefix="/jobs", tags=["Jobs"])
