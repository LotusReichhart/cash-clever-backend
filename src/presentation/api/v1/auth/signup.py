from fastapi import APIRouter, Depends, Request
from dependency_injector.wiring import inject, Provide

from src.app.container import Container
from src.core.exceptions import AppError, ValidationError, DoNotPermissionError
from src.core.limiter import limiter
from src.core.utils.validations.auth_validations import validate_name, validate_email, validate_password, validate_otp
from src.core.utils.validations.base_validation import is_empty
from src.domain.use_cases.auth import RequestSignupUseCase, SignupVerificationUseCase

from src.schemas.base_response import BaseResponse
from src.schemas.error_response import ErrorResponse

router = APIRouter(prefix="/signup", tags=["Signup"])


@router.post("")
@limiter.limit("6/minute")
@inject
async def request_registration(
        request: Request,
        request_signup_use_case: RequestSignupUseCase = Depends(Provide[Container.request_signup_use_case])):
    body = await request.json()
    email = body.get("email", "").strip()
    name = body.get("name", "").strip()
    password = body.get("password", "").strip()

    # === VALIDATION ===
    errors = {}

    name_error = validate_name(name)
    if name_error:
        errors["name"] = name_error

    email_error = validate_email(email)
    if email_error:
        errors["email"] = email_error

    password_error = validate_password(password)
    if password_error:
        errors["password"] = password_error

    if errors:
        raise ValidationError(errors=errors)
    try:
        data = await request_signup_use_case.execute(
            name=name,
            email=email,
            password=password
        )

        return BaseResponse(
            status=200,
            message="Mã xác thực đã gửi tới email của bạn, vui lòng kiểm tra cả thư mục spam nhé.",
            data=data
        )

    except AppError as e:
        print(f"ERRRRRRRR: {e}")
        return ErrorResponse(
            status=e.status_code,
            message=e.message,
            errors=e.errors
        )


@router.post("/verify")
@limiter.limit("6/minute")
@inject
async def registration_verification(
        request: Request,
        signup_verification_use_case: SignupVerificationUseCase = Depends(
            Provide[Container.signup_verification_use_case])):
    body = await request.json()
    email = body.get("email", "").strip()
    otp = body.get("otp", "").strip()

    # === VALIDATION ===
    if is_empty(email):
        raise DoNotPermissionError()

    errors = {}
    otp_error = validate_otp(otp)
    if otp_error:
        errors["otp"] = otp_error

    if errors:
        raise ValidationError(errors=errors)
    try:
        data = await signup_verification_use_case.execute(
            email=email,
            otp=otp,
        )

        return BaseResponse(
            status=201,
            message="Đăng ký tài khoản thành công",
            data=data
        )

    except AppError as e:
        return ErrorResponse(
            status=e.status_code,
            message=e.message,
            errors=e.errors
        )
