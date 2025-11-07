from fastapi import APIRouter

# from .create import router as create_router
from .get_all import router as get_all_router
from .get_by_id import router as get_by_id_router

category_router = APIRouter(prefix="/categories", tags=["Category"])

# category_router.include_router(create_router)
category_router.include_router(get_all_router)
category_router.include_router(get_by_id_router)