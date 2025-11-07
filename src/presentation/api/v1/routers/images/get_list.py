from fastapi import APIRouter, Depends, Request, Query
import logging

from dependency_injector.wiring import Provide, inject

from src.application.use_cases.images.get_list_images import GetListImagesUseCase
from src.core.constants import S3UploadType
from src.core.di import Container
from src.core.limiter import limiter

from src.domain.exceptions.app_exceptions import AppError

from src.presentation.api.v1.schemas.base_response import BaseResponse
from src.presentation.api.v1.schemas.error_response import ErrorResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="", tags=["Get List Images"])


@router.get("/")
@limiter.limit("25/minute")
@inject
async def get_list(
        request: Request,
        upload_type: S3UploadType = Query(
            alias="upload-type",
            description="Loại ảnh cần lấy"
        ),
        get_list_images_use_case: GetListImagesUseCase = Depends(
            Provide[Container.get_list_images_use_case])):
    user_payload = request.state.user
    user_id = user_payload.get("id")

    try:
        data = await get_list_images_use_case.execute(
            user_id=user_id,
            upload_type=upload_type
        )

        # logger.info(f"GetListImagesUseCase Running Data {data}")

        return BaseResponse(
            status=200,
            message="Lấy danh sách hình ảnh",
            data=data
        )

    except AppError as e:
        return ErrorResponse(
            status=e.status_code,
            message=e.message,
            errors=e.errors
        )
