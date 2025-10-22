from abc import ABC, abstractmethod


class OTPService(ABC):
    @abstractmethod
    def generate_otp(self, length: int = 6) -> str: ...

    @abstractmethod
    async def check_and_increment_limit(self, email: str) -> bool: ...

    @abstractmethod
    async def save_signup_otp(self, email: str, otp: str, name: str, password: str): ...

    @abstractmethod
    async def save_forgot_otp(self, email: str, otp: str, user_id: str): ...

    @abstractmethod
    async def verify_signup_otp(self, email: str, otp: str) -> dict[str, str]: ...

    @abstractmethod
    async def verify_forgot_otp(self, email: str, otp: str) -> dict[str, str]: ...

    @abstractmethod
    async def update_otp(self, email: str, otp: str) -> bool: ...
