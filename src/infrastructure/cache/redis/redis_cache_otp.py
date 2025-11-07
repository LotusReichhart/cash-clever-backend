from src.application.interfaces.cache import CacheOtp
from src.domain.exceptions.auth_exception import OtpIncorrectError

from src.infrastructure.cache.redis.redis_method import RedisMethod


class RedisCacheOtp(CacheOtp):
    def __init__(self, redis_method: RedisMethod):
        self.redis_method = redis_method

    async def check_and_increment_limit(self, email: str) -> bool:
        key = f"otp_limit:{email}"

        exists = await self.redis_method.exists(key)

        if exists:
            current = await self.redis_method.incr(key)
        else:
            current = 1
            await self.redis_method.set(key, current, expire_seconds=900)

        return current < 5

    async def save_signup_otp(self, email: str, otp: str, name: str, password: str):
        key = f"otp:{email}"
        data = {"otp": otp, "name": name, "password": password}
        await self.redis_method.set_json(key, data, expire_seconds=600)

    async def verify_signup_otp(self, email: str, otp: str) -> dict[str, str]:
        key_signup = f"otp:{email}"

        data = await self.redis_method.get_json(key_signup)

        if not data or data["otp"] != otp:
            raise OtpIncorrectError()

        name = data["name"]
        password = data["password"]

        await self.redis_method.delete(key_signup)
        await self.redis_method.delete(f"otp_limit:{email}")

        return {"email": email, "name": name, "password": password}

    async def save_forgot_otp(self, email: str, otp: str, user_id: str):
        key = f"otp:{email}"
        data = {"otp": otp, "user_id": user_id}
        await self.redis_method.set_json(key, data, expire_seconds=600)

    async def verify_forgot_otp(self, email: str, otp: str) -> dict[str, str]:
        key_forgot = f"otp:{email}"

        data = await self.redis_method.get_json(key_forgot)

        if not data or data["otp"] != otp:
            raise OtpIncorrectError()

        user_id = data["user_id"]

        await self.redis_method.delete(key_forgot)
        await self.redis_method.delete(f"otp_limit:{email}")

        return {"user_id": user_id}

    async def update_otp(self, email: str, otp: str) -> bool:
        key = f"otp:{email}"
        data = await self.redis_method.get_json(key)
        if not data:
            return False
        data["otp"] = otp
        await self.redis_method.set_json(key, data, expire_seconds=600)
        return True
