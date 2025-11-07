from fastapi import APIRouter

from .routers.auth import auth_router
from .routers.category import category_router

v1_router = APIRouter(prefix="/v1", tags=["version 1"])

v1_router.include_router(auth_router)
v1_router.include_router(category_router)
