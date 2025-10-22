import logging

from src.core.exceptions import ServerError, AppError
from src.domain.services import OTPService, TokenService

logger = logging.getLogger(__name__)


class PasswordVerificationUseCase:
    def __init__(self,
                 otp_service: OTPService,
                 token_service: TokenService):
        self.otp_service = otp_service
        self.token_service = token_service

    async def execute(self, email: str, otp: str) -> dict[str, str]:
        otp_data = await self.otp_service.verify_forgot_otp(email=email, otp=otp)

        user_id = otp_data["user_id"]

        try:
            reset_token = self.token_service.create_reset_token()

            await self.token_service.save_reset_token(
                token=reset_token,
                user_id=user_id
            )

            return {"reset_token": reset_token}

        except AppError:
            raise

        except Exception as e:
            logger.error(f"PasswordVerificationUseCase: {e}")
            raise ServerError() from e
