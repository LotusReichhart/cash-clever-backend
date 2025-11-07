from fastapi import APIRouter, Depends, Request
from dependency_injector.wiring import inject, Provide

from src.application.use_cases.auth.signin.signin_with_email_password import SigninWithEmailPasswordUseCase

from src.domain.exceptions.app_exceptions import AppError, BadRequestError

from src.core.limiter import limiter
from src.core.utils.validations.base_validation import is_empty

from src.domain.validations.user_validations import validate_email

from src.core.di import Container

from src.presentation.api.v1.schemas.base_response import BaseResponse
from src.presentation.api.v1.schemas.error_response import ErrorResponse

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
        raise BadRequestError(errors=errors)
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
