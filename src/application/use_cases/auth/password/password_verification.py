import logging

from src.application.interfaces.cache import CacheOtp, CacheToken
from src.domain.exceptions.app_exceptions import ServerError, AppError
from src.application.interfaces.services import TokenService

logger = logging.getLogger(__name__)


class PasswordVerificationUseCase:
    def __init__(self,
                 generate_token_service: TokenService,
                 cache_otp: CacheOtp,
                 cache_token: CacheToken):
        self.generate_token_service = generate_token_service
        self.cache_otp = cache_otp
        self.cache_token = cache_token

    async def execute(self, email: str, otp: str) -> dict[str, str]:
        otp_data = await self.cache_otp.verify_forgot_otp(email=email, otp=otp)

        user_id = otp_data["user_id"]

        try:
            reset_token = self.generate_token_service.create_reset_token()

            await self.cache_token.save_reset_token(
                token=reset_token,
                user_id=user_id
            )

            return {"reset_token": reset_token}

        except AppError:
            raise

        except Exception as e:
            logger.error(f"PasswordVerificationUseCase: {e}")
            raise ServerError() from e
