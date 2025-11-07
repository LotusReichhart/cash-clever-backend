import logging

from src.application.interfaces.cache import CacheOtp
from src.domain.exceptions.app_exceptions import ServerError, AppError
from src.domain.exceptions.auth_exception import TooManyOtpRequestsError
from src.application.interfaces.services import MailService, GenerateOtpService

logger = logging.getLogger(__name__)


class ResendOTPUseCase:
    def __init__(self,
                 generate_otp_service: GenerateOtpService,
                 cache_otp: CacheOtp,
                 mail_service: MailService):
        self.generate_otp_service = generate_otp_service
        self.cache_otp = cache_otp
        self.mail_service = mail_service

    async def execute(self, email: str):
        allowed = await self.cache_otp.check_and_increment_limit(email)
        if not allowed:
            raise TooManyOtpRequestsError()

        otp = self.generate_otp_service.generate_otp()
        success = await self.cache_otp.update_otp(email, otp)
        if not success:
            raise ServerError()

        template = self.mail_service.build_otp_template(otp)

        try:
            await self.mail_service.send_mail(
                to=email,
                subject=template["subject"],
                html=template["html"],
            )

        except AppError:
            raise

        except Exception as e:
            logger.error(f"ResendOTPUseCase: {e}")
            raise ServerError() from e
