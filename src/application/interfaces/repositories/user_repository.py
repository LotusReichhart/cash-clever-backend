from abc import ABC, abstractmethod

from src.domain.entities.user_entity import UserEntity

class UserRepository(ABC):
    """Interface for the User repository."""

    @abstractmethod
    async def create_user(self, user: UserEntity) -> UserEntity:
        raise NotImplementedError

    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def get_user_by_id(self, user_id: int) -> UserEntity | None:
        raise NotImplementedError

    @abstractmethod
    async def get_user_by_email(self, email: str) -> UserEntity | None:
        raise NotImplementedError

    @abstractmethod
    async def update_user_by_id(self, user_id: int, updates: dict) -> UserEntity | None:
        raise NotImplementedError