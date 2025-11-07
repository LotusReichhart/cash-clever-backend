import uuid
from datetime import datetime, timezone

from jwt import encode, decode, ExpiredSignatureError, InvalidTokenError

from src.application.interfaces.services import TokenService
from src.core.config.settings import settings


class JWTTokenService(TokenService):
    def create_access_token(self, user_id: int, signin_count: int, sign_out_count: int, refresh_jti: str) -> str:
        """Tạo Access Token."""
        payload = {
            "id": user_id,
            "signin_count": signin_count,
            "sign_out_count": sign_out_count,
            "exp": datetime.now(timezone.utc) + settings.ACCESS_TOKEN_LIFETIME,
            "iat": datetime.now(timezone.utc),
            "jti": str(uuid.uuid4()),  # jti của access token
            "refresh_jti": refresh_jti  # jti của refresh token tương ứng
        }
        return encode(payload, settings.JWT_ACCESS_SECRET, algorithm="HS256")

    def create_refresh_token(self, user_id: int, signin_count: int, sign_out_count: int) -> dict[str, str]:
        """Tạo Refresh Token và trả về (token, device_id)."""
        device_id = str(uuid.uuid4())  # Đây là jti của refresh token
        payload = {
            "id": user_id,
            "signin_count": signin_count,
            "sign_out_count": sign_out_count,
            "exp": datetime.now(timezone.utc) + settings.REFRESH_TOKEN_LIFETIME,
            "iat": datetime.now(timezone.utc),
            "jti": device_id  # Dùng jti làm định danh thiết bị/phiên
        }
        token = encode(payload, settings.JWT_REFRESH_SECRET, algorithm="HS256")
        return {"token": token, "device_id": device_id}

    def verify_access_token(self, token: str) -> dict | None:
        """Giải mã access token."""
        try:
            return decode(token, settings.JWT_ACCESS_SECRET, algorithms=["HS256"])
        except ExpiredSignatureError:
            return None
        except InvalidTokenError:
            return None

    def verify_refresh_token(self, token: str) -> dict | None:
        """Giải mã refresh token."""
        try:
            return decode(token, settings.JWT_REFRESH_SECRET, algorithms=["HS256"])
        except ExpiredSignatureError:
            return None
        except InvalidTokenError:
            return None

    def create_reset_token(self) -> str:
        return str(uuid.uuid4())
