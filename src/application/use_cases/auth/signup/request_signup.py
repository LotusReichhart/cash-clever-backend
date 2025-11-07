import logging

from src.application.interfaces.cache import CacheOtp
from src.domain.exceptions.app_exceptions import ServerError, AppError
from src.domain.exceptions.auth_exception import EmailAlreadyUsedError, TooManyOtpRequestsError
from src.application.interfaces.repositories import UserRepository
from src.application.interfaces.services import (
    MailService, PasswordHasherService, GenerateOtpService
)

logger = logging.getLogger(__name__)


class RequestSignupUseCase:
    def __init__(self,
                 user_repository: UserRepository,
                 generate_otp_service: GenerateOtpService,
                 cache_otp: CacheOtp,
                 mail_service: MailService,
                 password_hasher_service: PasswordHasherService):
        self.user_repository = user_repository
        self.generate_otp_service = generate_otp_service
        self.cache_otp = cache_otp
        self.mail_service = mail_service
        self.password_hasher_service = password_hasher_service

    async def execute(self, email: str, name: str, password: str) -> dict[str, str]:
        existing_user = await self.user_repository.exists_by_email(email)
        if existing_user:
            raise EmailAlreadyUsedError()

        try:
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

            hashed_pw = self.password_hasher_service.hash(password)
            await self.cache_otp.save_signup_otp(email=email, otp=otp, name=name, password=hashed_pw)

            return {"email": email}

        except AppError:
            raise

        except Exception as e:
            logger.error(f"RequestSignupUseCase unexpected error: {e}")
            raise ServerError() from e
