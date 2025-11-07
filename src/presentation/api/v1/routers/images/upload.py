from fastapi import APIRouter, Depends, Request, UploadFile, File, Form
import logging

from dependency_injector.wiring import Provide, inject

from src.application.use_cases.images.upload_image import UploadImageUseCase

from src.core.constants import S3UploadType
from src.core.di import Container
from src.core.limiter import limiter

from src.domain.exceptions.app_exceptions import AppError

from src.presentation.api.v1.schemas.base_response import BaseResponse
from src.presentation.api.v1.schemas.error_response import ErrorResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="", tags=["Upload Image"])


@router.post("/")
@limiter.limit("25/minute")
@inject
async def upload(
        request: Request,
        file: UploadFile = File(..., description="File ảnh cần upload"),
        upload_type: S3UploadType = Form(
            alias="upload-type",
            description="Loại ảnh upload"
        ),
        upload_image_use_case: UploadImageUseCase = Depends(
            Provide[Container.upload_image_use_case])):
    user_payload = request.state.user
    user_id = user_payload.get("id")

    try:
        data = await upload_image_use_case.execute(
            user_id=user_id,
            image_file=file,
            upload_type=upload_type
        )

        # logger.info(f"UploadImageUseCase Running Data {data}")

        return BaseResponse(
            status=201,
            message="Tải hình ảnh lên thành công",
            data=data
        )

    except AppError as e:
        return ErrorResponse(
            status=e.status_code,
            message=e.message,
            errors=e.errors
        )
