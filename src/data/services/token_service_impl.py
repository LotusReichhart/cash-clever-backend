from typing import Tuple

import jwt
import uuid
import hashlib

from datetime import datetime, timezone

from src.core.config import settings
from src.domain.exceptions.auth_exception import TokenExpiredError, TokenInvalidError
from src.domain.services import TokenService
from src.data.cache.redis_service import RedisService


class TokenServiceImpl(TokenService):
    def __init__(self, redis_service: RedisService):
        self.redis_service = redis_service

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
        return jwt.encode(payload, settings.JWT_ACCESS_SECRET, algorithm="HS256")

    def create_refresh_token(self, user_id: int, signin_count: int, sign_out_count: int) -> Tuple[str, str]:
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
        token = jwt.encode(payload, settings.JWT_REFRESH_SECRET, algorithm="HS256")
        return token, device_id

    @staticmethod
    def hash_token(token: str) -> str:
        """Hash token để lưu trữ an toàn."""
        return hashlib.sha256(token.encode()).hexdigest()

    async def save_refresh_token(self, user_id: int, device_id: str, token: str):
        """Lưu hash của refresh token vào Redis Hash."""
        key = f"user_sessions:{user_id}"
        hashed_token = self.hash_token(token)

        # Lưu trữ theo cấu trúc: HSET user_sessions:{user_id} {device_id} {hashed_token}
        await self.redis_service.hset(key, device_id, hashed_token)
        # Đặt TTL cho cả hash key để tự động dọn dẹp
        await self.redis_service.expire(key, int(settings.REFRESH_TOKEN_LIFETIME.total_seconds()))

    async def get_refresh_token_hash(self, user_id: int, device_id: str) -> str | None:
        """Lấy hash của refresh token từ Redis."""
        key = f"user_sessions:{user_id}"
        hashed_token = await self.redis_service.hget(key, device_id)

        if hashed_token is None:
            return None

        # Nếu là bytes thì decode, nếu đã là str thì giữ nguyên
        if isinstance(hashed_token, bytes):
            return hashed_token.decode("utf-8")

        return hashed_token

    async def delete_refresh_token(self, user_id: int, device_id: str):
        """Xóa một refresh token cụ thể (sign_out 1 thiết bị)."""
        key = f"user_sessions:{user_id}"
        await self.redis_service.hdel(key, device_id)

    async def delete_all_refresh_tokens(self, user_id: int):
        """Xóa tất cả refresh token (sign_out tất cả thiết bị)."""
        key = f"user_sessions:{user_id}"
        await self.redis_service.delete(key)

    def verify_token(self, token: str, secret: str) -> dict | None:
        """Giải mã một token bất kỳ."""
        try:
            return jwt.decode(token, secret, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError()
        except jwt.InvalidTokenError:
            raise TokenInvalidError()

    def create_reset_token(self) -> str:
        return str(uuid.uuid4())

    async def save_reset_token(self, token: str, user_id: str):
        hashed = self.hash_token(token)
        key = f"reset_token:{hashed}"
        await self.redis_service.set_json(key, {"user_id": user_id}, expire_seconds=600)

    async def verify_reset_token(self, token: str) -> dict[str, str] | None:
        hashed = self.hash_token(token)
        key = f"reset_token:{hashed}"
        data = await self.redis_service.get_json(key)
        if not data:
            return None
        await self.delete_reset_token(token)
        return {"user_id": data["user_id"]}

    async def delete_reset_token(self, token: str):
        hashed = self.hash_token(token)
        await self.redis_service.delete(f"reset_token:{hashed}")
