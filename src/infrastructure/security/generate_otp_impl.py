import secrets

from src.application.interfaces.services import GenerateOtpService


class GenerateOtpImpl(GenerateOtpService):
    def generate_otp(self, length: int = 6) -> str:
        return ''.join(str(secrets.randbelow(10)) for _ in range(length))
