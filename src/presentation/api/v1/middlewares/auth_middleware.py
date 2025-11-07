import logging

import jwt
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from src.core.config import settings
from src.presentation.api.v1.schemas.error_response import ErrorResponse

logger = logging.getLogger(__name__)


from src.domain.exceptions.app_exceptions import UnauthorizedError

# --- Các đường dẫn công khai không cần xác thực ---
PUBLIC_PATHS = [
    "/api/v1/auth/signin",
    "/api/v1/auth/signup",
    "/api/v1/auth/password",
    "/api/v1/auth/otp",
    "/api/v1/auth/refresh",
    "/api/v1/auth/google",
]


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        try:
            # --- Bỏ qua các path public ---
            if any(request.url.path.startswith(path) for path in PUBLIC_PATHS):
                return await call_next(request)

            # --- Lấy và kiểm tra header Authorization ---
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                raise UnauthorizedError()

            try:
                scheme, token = auth_header.split()
                if scheme.lower() != "bearer":
                    raise UnauthorizedError()
            except ValueError:
                raise UnauthorizedError()

            # --- Giải mã token ---
            try:
                payload = jwt.decode(
                    token,
                    key=settings.JWT_ACCESS_SECRET,
                    algorithms=["HS256"]
                )
            except jwt.ExpiredSignatureError as e:
                logger.warning(f"Expired JWT: {e}")
                raise UnauthorizedError()
            except jwt.InvalidTokenError:
                raise UnauthorizedError()

            # --- Gắn payload vào request.state ---
            request.state.user = {
                "id": payload["id"],
                "signin_count": payload["signin_count"],
                "sign_out_count": payload["sign_out_count"],
                "refresh_jti": payload["refresh_jti"],
            }

            # --- Tiếp tục xử lý request ---
            return await call_next(request)

        except UnauthorizedError as e:
            # Xử lý 401 lỗi xác thực
            return ErrorResponse(
                status=e.status_code,
                message=e.message,
                errors=e.errors
            )

        except Exception as e:
            # Bắt mọi lỗi không lường trước
            logger.exception("Unhandled error in AuthMiddleware")
            return ErrorResponse(
                status=500,
                message="Internal Server Error",
                errors={"system": str(e)}
            )
