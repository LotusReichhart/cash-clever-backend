from fastapi import APIRouter, Depends, Request
from dependency_injector.wiring import inject, Provide

from src.application.use_cases.auth.sign_out.sign_out_and_clear_token import SignOutAndClearTokenUseCase

from src.domain.exceptions.app_exceptions import AppError

from src.core.limiter import limiter

from src.core.di import Container

from src.presentation.api.v1.schemas.base_response import BaseResponse
from src.presentation.api.v1.schemas.error_response import ErrorResponse

router = APIRouter(prefix="/sign-out", tags=["Sign Out"])


@router.get("")
@limiter.limit("3 per 1 minutes")
@inject
async def sign_out(
        request: Request,
        sign_out_and_clear_token_use_case: SignOutAndClearTokenUseCase = Depends(
            Provide[Container.sign_out_and_clear_token_use_case])):
    user_payload = request.state.user

    user_id = user_payload.get("id")
    signin_count = user_payload.get("signin_count")
    sign_out_count = user_payload.get("sign_out_count")

    try:
        await sign_out_and_clear_token_use_case.execute(
            user_id=user_id,
            signin_count=signin_count,
            sign_out_count=sign_out_count
        )

        return BaseResponse(
            status=200,
            message="Đã đăng xuất tài khoản.",
            data=None
        )

    except AppError as e:
        return ErrorResponse(
            status=e.status_code,
            message=e.message,
            errors=e.errors
        )
