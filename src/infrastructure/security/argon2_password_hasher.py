from argon2 import PasswordHasher

from src.application.interfaces.services.password_hasher_service import PasswordHasherService


class Argon2PasswordHasher(PasswordHasherService):
    def __init__(self):
        self.ph = PasswordHasher()

    def hash(self, password: str) -> str:
        return self.ph.hash(password)

    def verify(self, hashed_password: str, password: str) -> bool:
        try:
            return self.ph.verify(hashed_password, password)
        except Exception:
            return False
