from abc import ABC, abstractmethod
from typing import Tuple


class TokenService(ABC):
    @abstractmethod
    def create_access_token(self, user_id: int, signin_count: int, sign_out_count: int, refresh_jti: str) -> str: ...

    @abstractmethod
    def create_refresh_token(self, user_id: int, signin_count: int, sign_out_count: int) -> Tuple[str, str]: ...

    @staticmethod
    @abstractmethod
    def hash_token(token: str) -> str: ...

    @abstractmethod
    async def save_refresh_token(self, user_id: int, device_id: str, token: str): ...

    @abstractmethod
    async def get_refresh_token_hash(self, user_id: int, device_id: str) -> str | None: ...

    @abstractmethod
    async def delete_refresh_token(self, user_id: int, device_id: str): ...

    @abstractmethod
    async def delete_all_refresh_tokens(self, user_id: int): ...

    @abstractmethod
    def verify_token(self, token: str, secret: str) -> dict | None: ...

    @abstractmethod
    def create_reset_token(self) -> str: ...

    @abstractmethod
    async def save_reset_token(self, token: str, user_id: str, ): ...

    @abstractmethod
    async def verify_reset_token(self, token: str) -> dict[str, str] | None: ...

    @abstractmethod
    async def delete_reset_token(self, token: str): ...
