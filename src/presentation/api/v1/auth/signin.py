from fastapi import APIRouter, Depends, Request
from dependency_injector.wiring import inject, Provide

from src.app.container import Container
from src.core.exceptions import AppError, ValidationError
from src.core.limiter import limiter
from src.core.utils.validations.auth_validations import validate_email
from src.core.utils.validations.base_validation import is_empty
from src.domain.use_cases.auth import SigninWithEmailPasswordUseCase

from src.schemas.base_response import BaseResponse
from src.schemas.error_response import ErrorResponse

router = APIRouter(prefix="/signin", tags=["Signin"])


@router.post("")
@limiter.limit("6/minute")
@inject
async def signin_with_email(
        request: Request,
        signin_with_email_password_use_case: SigninWithEmailPasswordUseCase = Depends(
            Provide[Container.signin_with_email_password_use_case])):
    body = await request.json()
    email = body.get("email", "").strip()
    password = body.get("password", "").strip()

    errors = {}

    email_error = validate_email(email)
    if email_error:
        errors["email"] = email_error

    if is_empty(password):
        errors["password"] = "Vui lòng nhập mật khẩu."

    if errors:
        raise ValidationError(errors=errors)
    try:
        data = await signin_with_email_password_use_case.execute(
            email=email,
            password=password
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
