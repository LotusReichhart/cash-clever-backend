import logging

from src.core.exceptions import ServerError, AppError
from src.domain.exceptions.auth_exception import TooManyOtpRequestsError, EmailNotRegisteredError
from src.domain.repositories import UserRepository
from src.domain.services import OTPService, MailService

logger = logging.getLogger(__name__)


class RequestForgotPasswordUseCase:
    def __init__(self,
                 user_repository: UserRepository,
                 otp_service: OTPService,
                 mail_service: MailService):
        self.user_repository = user_repository
        self.otp_service = otp_service
        self.mail_service = mail_service

    async def execute(self, email: str) -> dict[str, str]:
        try:
            user = await self.user_repository.get_user_by_email(email)

            if not user:
                raise EmailNotRegisteredError()

            allowed = await self.otp_service.check_and_increment_limit(email)

            if not allowed:
                raise TooManyOtpRequestsError()

            otp = self.otp_service.generate_otp()
            template = self.mail_service.build_otp_template(otp)
            await self.mail_service.send_mail(
                to=email,
                subject=template["subject"],
                html=template["html"],
            )

            await self.otp_service.save_forgot_otp(email=email, otp=otp, user_id=user.id)
            return {"email": email}

        except AppError:
            raise

        except Exception as e:
            logger.error(f"RequestForgotPasswordUseCase: {e}")
            raise ServerError() from e
