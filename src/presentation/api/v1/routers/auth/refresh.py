from fastapi import APIRouter, Depends, Request
from dependency_injector.wiring import inject, Provide

from src.application.use_cases.auth.refresh.refresh_signin import RefreshSigninUseCase

from src.domain.exceptions.app_exceptions import AppError, UnauthorizedError

from src.core.limiter import limiter

from src.core.di import Container

from src.presentation.api.v1.schemas.base_response import BaseResponse
from src.presentation.api.v1.schemas.error_response import ErrorResponse

router = APIRouter(prefix="/refresh", tags=["OTP"])


@router.post("")
@limiter.limit("2 per 30 minutes")
@inject
async def refresh_signin(
        request: Request,
        refresh_signin_use_case: RefreshSigninUseCase = Depends(Provide[Container.refresh_signin_use_case])):
    body = await request.json()
    refresh_token = body.get("refresh_token", "").strip()

    if not refresh_token:
        raise UnauthorizedError()
    try:
        data = await refresh_signin_use_case.execute(refresh_token)

        return BaseResponse(
            status=200,
            message="Đã tự động đăng nhập.",
            data=data
        )

    except AppError as e:
        return ErrorResponse(
            status=e.status_code,
            message=e.message,
            errors=e.errors
        )
