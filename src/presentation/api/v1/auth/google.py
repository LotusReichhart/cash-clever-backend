from fastapi import APIRouter, Depends, Request
from dependency_injector.wiring import inject, Provide

from src.app.container import Container
from src.core.exceptions import AppError, ValidationError
from src.core.limiter import limiter
from src.core.utils.validations.base_validation import is_empty
from src.domain.use_cases.auth import HandleGoogleAuthUseCase

from src.schemas.base_response import BaseResponse
from src.schemas.error_response import ErrorResponse

router = APIRouter(prefix="/google", tags=["Google Authentication"])


@router.post("")
@limiter.limit("6/minute")
@inject
async def google_auth(
        request: Request,
        handle_google_auth_use_case: HandleGoogleAuthUseCase = Depends(Provide[Container.handle_google_auth_use_case])):
    body = await request.json()
    user_id_token = body.get("user_id_token", "").strip()

    errors = {}

    user_id_token_error = is_empty(user_id_token)
    if user_id_token_error:
        errors["token"] = user_id_token_error

    if errors:
        raise ValidationError(errors=errors)
    try:
        data = await handle_google_auth_use_case.execute(
            user_id_token=user_id_token
        )

        return BaseResponse(
            status=200,
            message="Đăng nhập tài khoản thành công",
            data=data
        )
    except AppError as e:
        return ErrorResponse(
            status=e.status_code,
            message=e.message,
            errors=e.errors
        )
