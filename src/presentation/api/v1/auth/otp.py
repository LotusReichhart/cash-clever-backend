from fastapi import APIRouter, Depends, Request
from dependency_injector.wiring import inject, Provide

from src.app.container import Container
from src.core.exceptions import AppError, ValidationError
from src.core.limiter import limiter
from src.core.utils.validations.auth_validations import validate_email
from src.domain.use_cases.auth import ResendOTPUseCase
from src.schemas.base_response import BaseResponse
from src.schemas.error_response import ErrorResponse

router = APIRouter(prefix="/otp", tags=["OTP"])


@router.post("/resend")
@limiter.limit("6/minute")
@inject
async def resend_otp(
        request: Request,
        resend_otp_use_case: ResendOTPUseCase = Depends(Provide[Container.resend_otp_use_case])):
    body = await request.json()
    email = body.get("email", "").strip()

    errors = {}

    email_error = validate_email(email)
    if email_error:
        errors["email"] = email_error

    if errors:
        raise ValidationError(errors=errors)
    try:
        await resend_otp_use_case.execute(email)

        return BaseResponse(
            status=200,
            message="Mã xác thực đã gửi tới email của bạn, vui lòng kiểm tra cả thư mục spam nhé.",
            data=None
        )

    except AppError as e:
        return ErrorResponse(
            status=e.status_code,
            message=e.message,
            errors=e.errors
        )
