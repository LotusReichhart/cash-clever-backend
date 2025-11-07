import hashlib

from src.application.interfaces.cache import CacheToken
from src.infrastructure.cache.redis.redis_method import RedisMethod
from src.core.config.settings import settings


class RedisCacheToken(CacheToken):
    def __init__(self, redis_method: RedisMethod):
        self.redis_method = redis_method

    def hash_token(self, token: str) -> str:
        """Hash token để lưu trữ an toàn."""
        return hashlib.sha256(token.encode()).hexdigest()

    async def save_refresh_token(self, user_id: int, device_id: str, token: str):
        """Lưu hash của refresh token vào Redis Hash."""
        key = f"user_sessions:{user_id}"
        hashed_token = self.hash_token(token)

        # Lưu trữ theo cấu trúc: HSET user_sessions:{user_id} {device_id} {hashed_token}
        await self.redis_method.hset(key, device_id, hashed_token)
        # Đặt TTL cho cả hash key để tự động dọn dẹp
        await self.redis_method.expire(key, int(settings.REFRESH_TOKEN_LIFETIME.total_seconds()))

    async def get_refresh_token_hash(self, user_id: int, device_id: str) -> str | None:
        """Lấy hash của refresh token từ Redis."""
        key = f"user_sessions:{user_id}"
        hashed_token = await self.redis_method.hget(key, device_id)

        if hashed_token is None:
            return None

        # Nếu là bytes thì decode, nếu đã là str thì giữ nguyên
        if isinstance(hashed_token, bytes):
            return hashed_token.decode("utf-8")

        return hashed_token

    async def delete_refresh_token(self, user_id: int, device_id: str):
        """Xóa một refresh token cụ thể (sign_out 1 thiết bị)."""
        key = f"user_sessions:{user_id}"
        await self.redis_method.hdel(key, device_id)

    async def delete_all_refresh_tokens(self, user_id: int):
        """Xóa tất cả refresh token (sign_out tất cả thiết bị)."""
        key = f"user_sessions:{user_id}"
        await self.redis_method.delete(key)

    async def save_reset_token(self, token: str, user_id: str):
        hashed = self.hash_token(token)
        key = f"reset_token:{hashed}"
        await self.redis_method.set_json(key, {"user_id": user_id}, expire_seconds=600)

    async def verify_reset_token(self, token: str) -> dict[str, str] | None:
        hashed = self.hash_token(token)
        key = f"reset_token:{hashed}"
        data = await self.redis_method.get_json(key)
        if not data:
            return None
        await self.delete_reset_token(token)
        return {"user_id": data["user_id"]}

    async def delete_reset_token(self, token: str):
        hashed = self.hash_token(token)
        await self.redis_method.delete(f"reset_token:{hashed}")
