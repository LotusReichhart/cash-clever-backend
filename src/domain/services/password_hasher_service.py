from abc import abstractmethod, ABC


class PasswordHasherService(ABC):
    @abstractmethod
    def hash(self, password: str) -> str: ...

    @abstractmethod
    def verify(self, hashed_password: str, password: str) -> bool: ...