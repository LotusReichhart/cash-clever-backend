from abc import ABC, abstractmethod


class TokenService(ABC):
    @abstractmethod
    def create_access_token(self, user_id: int, signin_count: int, sign_out_count: int, refresh_jti: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def create_refresh_token(self, user_id: int, signin_count: int, sign_out_count: int) -> dict[str, str]:
        raise NotImplementedError

    @abstractmethod
    def verify_access_token(self, token: str) -> dict | None:
        raise NotImplementedError

    @abstractmethod
    def verify_refresh_token(self, token: str) -> dict | None:
        raise NotImplementedError

    @abstractmethod
    def create_reset_token(self) -> str:
        raise NotImplementedError
