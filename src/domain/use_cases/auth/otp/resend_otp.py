import logging

from src.core.exceptions import ServerError, AppError
from src.domain.exceptions.auth_exception import TooManyOtpRequestsError
from src.domain.services import OTPService, MailService

logger = logging.getLogger(__name__)


class ResendOTPUseCase:
    def __init__(self,
                 otp_service: OTPService,
                 mail_service: MailService):
        self.otp_service = otp_service
        self.mail_service = mail_service

    async def execute(self, email: str):
        allowed = await self.otp_service.check_and_increment_limit(email)
        if not allowed:
            raise TooManyOtpRequestsError()

        otp = self.otp_service.generate_otp()
        success = await self.otp_service.update_otp(email, otp)
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
