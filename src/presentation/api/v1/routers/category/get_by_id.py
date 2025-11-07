from fastapi import APIRouter, Depends, Request, Path
import logging

from dependency_injector.wiring import Provide, inject

from src.application.use_cases.category.get_category_by_id import GetCategoryByIdUseCase
from src.core.di import Container
from src.core.limiter import limiter

from src.domain.exceptions.app_exceptions import AppError

from src.presentation.api.v1.schemas.base_response import BaseResponse
from src.presentation.api.v1.schemas.error_response import ErrorResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="", tags=["Get By Id"])


@router.get("/{id}")
@limiter.limit("25/minute")
@inject
async def get_by_id(
        request: Request,
        id: int = Path(ge=1, description="ID của danh mục cần lấy"),
        get_category_by_id_use_case: GetCategoryByIdUseCase = Depends(
            Provide[Container.get_category_by_id_use_case])):
    user_payload = request.state.user
    user_id = user_payload.get("id")

    try:
        data = await get_category_by_id_use_case.execute(
            category_id=id,
            user_id=user_id,
        )

        # logger.info(f"GetCategoryByIdUseCase Running Data {data}")

        return BaseResponse(
            status=200,
            message="Lấy thông tin danh mục thành công",
            data=data
        )

    except AppError as e:
        return ErrorResponse(
            status=e.status_code,
            message=e.message,
            errors=e.errors
        )
