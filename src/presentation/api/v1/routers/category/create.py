from fastapi import APIRouter, Depends, Request
from dependency_injector.wiring import inject, Provide

from src.application.use_cases.category.create_category import CreateCategoryUseCase
from src.core.di import Container
from src.core.limiter import limiter
from src.domain.exceptions.app_exceptions import BadRequestError, AppError
from src.domain.validations.category_validations import validate_name
from src.presentation.api.v1.schemas.base_response import BaseResponse
from src.presentation.api.v1.schemas.error_response import ErrorResponse

router = APIRouter(prefix="", tags=["Create"])


@router.post("/")
@limiter.limit("6/minute")
@inject
async def create_category(
        request: Request,
        create_category_use_case: CreateCategoryUseCase = Depends(
            Provide[Container.create_category_use_case])):
    body = await request.json()
    name = body.get("name", "").strip()
    icon_url = body.get("icon_url", "").strip()
    parent_id_raw = body.get("parent_id", "").strip()
    parent_id = None

    user_payload = request.state.user
    user_id = user_payload.get("id")

    # === VALIDATION ===
    errors = {}

    name_error = validate_name(name)
    if name_error:
        errors["name"] = name_error

    if parent_id_raw is not None and parent_id_raw != "":
        try:
            parent_id = int(parent_id_raw)
        except (ValueError, TypeError):
            pass

    if errors:
        raise BadRequestError(errors=errors)
    try:
        await create_category_use_case.execute(
            name=name,
            user_id=user_id,
            parent_id=parent_id,
            icon_url=icon_url
        )

        return BaseResponse(
            status=201,
            message="Tạo mới danh mục thành công",
            data=None
        )

    except AppError as e:
        return ErrorResponse(
            status=e.status_code,
            message=e.message,
            errors=e.errors
        )
