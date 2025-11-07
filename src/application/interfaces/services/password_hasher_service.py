from abc import ABC, abstractmethod


class PasswordHasherService(ABC):
    @abstractmethod
    def hash(self, password: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def verify(self, hashed_password: str, password: str) -> bool:
        raise NotImplementedError
