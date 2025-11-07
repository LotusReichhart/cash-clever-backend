from abc import ABC, abstractmethod


class CacheOtp(ABC):
    @abstractmethod
    async def check_and_increment_limit(self, email: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def save_signup_otp(self, email: str, otp: str, name: str, password: str):
        raise NotImplementedError

    @abstractmethod
    async def save_forgot_otp(self, email: str, otp: str, user_id: str):
        raise NotImplementedError

    @abstractmethod
    async def verify_signup_otp(self, email: str, otp: str) -> dict[str, str]:
        raise NotImplementedError

    @abstractmethod
    async def verify_forgot_otp(self, email: str, otp: str) -> dict[str, str]:
        raise NotImplementedError

    @abstractmethod
    async def update_otp(self, email: str, otp: str) -> bool:
        raise NotImplementedError
