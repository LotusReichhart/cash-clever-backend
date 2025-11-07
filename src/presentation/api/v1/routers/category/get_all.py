from typing import Optional

from fastapi import APIRouter, Depends, Request, Query
import logging

from dependency_injector.wiring import Provide, inject

from src.application.use_cases.category.get_category_tree import GetCategoryTreeUseCase
from src.core.di import Container
from src.core.limiter import limiter

from src.domain.exceptions.app_exceptions import AppError

from src.presentation.api.v1.schemas.base_response import BaseResponse
from src.presentation.api.v1.schemas.error_response import ErrorResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="", tags=["Get All"])


@router.get("/")
@limiter.limit("25/minute")
@inject
async def get_all_categories(
        request: Request,
        q: Optional[str] = Query(None, min_length=1),
        limit: int = Query(12, ge=1),
        offset: int = Query(0, ge=0),
        get_category_tree_use_case: GetCategoryTreeUseCase = Depends(
            Provide[Container.get_category_tree_use_case])):
    user_payload = request.state.user
    user_id = user_payload.get("id")

    try:
        data = await get_category_tree_use_case.execute(
            user_id=user_id,
            limit=limit,
            offset=offset,
            search_term=q
        )
        message = "Tìm kiếm thành công" if q else "Lấy danh sách danh mục thành công"
        # logger.info(f"GetCategoryTreeUseCase Running Offset {offset} Data {data['categories']}")

        return BaseResponse(
            status=200,
            message=message,
            data=data
        )

    except AppError as e:
        return ErrorResponse(
            status=e.status_code,
            message=e.message,
            errors=e.errors
        )
