from abc import ABC, abstractmethod


class MailService(ABC):
    @abstractmethod
    async def send_mail(self, to: str, subject: str, html: str) -> None: ...

    @abstractmethod
    def build_otp_template(self, otp: str) -> dict[str, str]: ...
