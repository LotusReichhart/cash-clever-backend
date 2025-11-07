import logging

from src.application.interfaces.cache import CacheOtp
from src.domain.exceptions.app_exceptions import ServerError, AppError
from src.domain.exceptions.auth_exception import TooManyOtpRequestsError, EmailNotRegisteredError
from src.application.interfaces.repositories import UserRepository
from src.application.interfaces.services import (
    MailService, GenerateOtpService
)

logger = logging.getLogger(__name__)


class RequestForgotPasswordUseCase:
    def __init__(self,
                 user_repository: UserRepository,
                 generate_otp_service: GenerateOtpService,
                 cache_otp: CacheOtp,
                 mail_service: MailService):
        self.user_repository = user_repository
        self.generate_otp_service = generate_otp_service
        self.cache_otp = cache_otp
        self.mail_service = mail_service

    async def execute(self, email: str) -> dict[str, str]:
        try:
            user = await self.user_repository.get_user_by_email(email)

            if not user:
                raise EmailNotRegisteredError()

            allowed = await self.cache_otp.check_and_increment_limit(email)

            if not allowed:
                raise TooManyOtpRequestsError()

            otp = self.generate_otp_service.generate_otp()
            template = self.mail_service.build_otp_template(otp)
            await self.mail_service.send_mail(
                to=email,
                subject=template["subject"],
                html=template["html"],
            )

            await self.cache_otp.save_forgot_otp(email=email, otp=otp, user_id=user.id)
            return {"email": email}

        except AppError:
            raise

        except Exception as e:
            logger.error(f"RequestForgotPasswordUseCase: {e}")
            raise ServerError() from e
