from abc import ABC, abstractmethod


class CacheToken(ABC):
    @abstractmethod
    def hash_token(self, token: str) -> str:
        raise NotImplementedError

    @abstractmethod
    async def save_refresh_token(self, user_id: int, device_id: str, token: str):
        raise NotImplementedError

    @abstractmethod
    async def get_refresh_token_hash(self, user_id: int, device_id: str) -> str | None:
        raise NotImplementedError

    @abstractmethod
    async def delete_refresh_token(self, user_id: int, device_id: str):
        raise NotImplementedError

    @abstractmethod
    async def delete_all_refresh_tokens(self, user_id: int):
        raise NotImplementedError

    @abstractmethod
    async def save_reset_token(self, token: str, user_id: str, ):
        raise NotImplementedError

    @abstractmethod
    async def verify_reset_token(self, token: str) -> dict[str, str] | None:
        raise NotImplementedError

    @abstractmethod
    async def delete_reset_token(self, token: str):
        raise NotImplementedError
