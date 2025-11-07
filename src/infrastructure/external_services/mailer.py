import aiosmtplib
from email.mime.text import MIMEText

from src.core.config.settings import settings


class MailTransporter:
    def __init__(self):
        self.host = settings.MAIL_HOST
        self.port = settings.MAIL_PORT
        self.user = settings.MAIL_USER
        self.password = settings.MAIL_PASSWORD
        self.sender = settings.MAIL_SENDER_NAME

    async def send_mail(self, to: str, subject: str, html: str):
        message = MIMEText(html, "html")
        message["From"] = self.sender
        message["To"] = to
        message["Subject"] = subject

        try:
            await aiosmtplib.send(
                message,
                hostname=self.host,
                port=self.port,
                username=self.user,
                password=self.password,
                start_tls=True,
            )
            return True
        except Exception as e:
            print(f"Mail sending failed: {e}")
            return False
