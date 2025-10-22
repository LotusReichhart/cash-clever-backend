from src.domain.services import PasswordHasherService
from argon2 import PasswordHasher

class PasswordHasherServiceImpl(PasswordHasherService):
    def __init__(self):
        self.ph = PasswordHasher()

    def hash(self, password: str) -> str:
        return self.ph.hash(password)

    def verify(self, hashed_password: str, password: str) -> bool:
        try:
            return self.ph.verify(hashed_password, password)
        except Exception:
            return False