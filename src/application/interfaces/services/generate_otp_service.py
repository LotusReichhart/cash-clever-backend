from abc import ABC, abstractmethod


class GenerateOtpService(ABC):
    @abstractmethod
    def generate_otp(self, length: int = 6) -> str:
        raise NotImplementedError
