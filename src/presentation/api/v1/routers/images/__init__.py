from fastapi import APIRouter

from .get_list import router as get_list
from .upload import router as upload

images_router = APIRouter(prefix="/images", tags=["Image"])

images_router.include_router(get_list)
images_router.include_router(upload)
