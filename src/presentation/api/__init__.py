from fastapi import APIRouter

from .v1 import v1_router

api_router = APIRouter(prefix="/api", tags=["APIs"])

api_router.include_router(v1_router)