from fastapi import APIRouter, Depends, Request
from dependency_injector.wiring import inject, Provide

from src.app.container import Container
from src.core.exceptions import AppError, ValidationError, DoNotPermissionError
from src.core.limiter import limiter
from src.core.utils.validations.auth_validations import validate_email, validate_otp, validate_password
from src.domain.use_cases.auth import RequestForgotPasswordUseCase, PasswordVerificationUseCase, ChangePasswordUseCase

from src.schemas.base_response import BaseResponse
from src.schemas.error_response import ErrorResponse

router = APIRouter(prefix="/password", tags=["Password"])


@router.post("/forgot")
@limiter.limit("6/minute")
@inject
async def request_forgot_password(
        request: Request,
        request_forgot_password_use_case: RequestForgotPasswordUseCase = Depends(
            Provide[Container.request_forgot_password_use_case])):
    body = await request.json()
    email = body.get("email", "").strip()

    # === VALIDATION ===
    errors = {}

    email_error = validate_email(email)
    if email_error:
        errors["email"] = email_error

    if errors:
        raise ValidationError(errors=errors)
    try:
        data = await request_forgot_password_use_case.execute(
            email=email
        )

        return BaseResponse(
            status=200,
            message="Mã xác thực đã gửi tới email của bạn, vui lòng kiểm tra cả thư mục spam nhé.",
            data=data
        )

    except AppError as e:
        return ErrorResponse(
            status=e.status_code,
            message=e.message,
            errors=e.errors
        )


@router.post("/verify")
@limiter.limit("6/minute")
@inject
async def forgot_password_verification(
        request: Request,
        password_verification_use_case: PasswordVerificationUseCase = Depends(
            Provide[Container.password_verification_use_case])):
    body = await request.json()
    email = body.get("email", "").strip()
    otp = body.get("otp", "").strip()

    # === VALIDATION ===
    errors = {}

    email_error = validate_email(email)
    if email_error:
        errors["email"] = email_error

    otp_error = validate_otp(otp)
    if otp_error:
        errors["otp"] = otp_error

    if errors:
        raise ValidationError(errors=errors)
    try:
        data = await password_verification_use_case.execute(
            email=email,
            otp=otp,
        )

        return BaseResponse(
            status=200,
            message="Hoàn thành xác thực",
            data=data
        )

    except AppError as e:
        return ErrorResponse(
            status=e.status_code,
            message=e.message,
            errors=e.errors
        )


@router.post("/reset")
@limiter.limit("6/minute")
@inject
async def change_password(
        request: Request,
        change_password_use_case: ChangePasswordUseCase = Depends(Provide[Container.change_password_use_case])):
    body = await request.json()
    reset_token = str(body.get("reset_token") or "").strip()
    new_password = body.get("new_password", "").strip()
    confirm_password = body.get("confirm_password", "").strip()

    if not reset_token:
        raise DoNotPermissionError()

    # === VALIDATION ===
    errors = {}

    new_password_error = validate_password(new_password)
    if new_password_error:
        errors["new_password"] = new_password_error

    if confirm_password != new_password:
        errors["confirm_password"] = "Mật khẩu xác nhận không khớp."

    if errors:
        raise ValidationError(errors=errors)
    try:
        await change_password_use_case.execute(
            reset_token=reset_token,
            new_password=new_password
        )

        return BaseResponse(
            status=200,
            message="Mật khẩu của bạn đã được thay đổi thành công.",
            data=None
        )

    except AppError as e:
        return ErrorResponse(
            status=e.status_code,
            message=e.message,
            errors=e.errors
        )
