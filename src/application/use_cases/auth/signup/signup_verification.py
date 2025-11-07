import logging

from src.application.interfaces.cache import CacheOtp, CacheToken
from src.domain.exceptions.app_exceptions import ServerError, AppError
from src.domain.entities import UserEntity, UserStatus
from src.application.interfaces.repositories import UserRepository
from src.application.interfaces.services import TokenService

logger = logging.getLogger(__name__)


class SignupVerificationUseCase:
    def __init__(self,
                 user_repository: UserRepository,
                 cache_otp: CacheOtp,
                 token_service: TokenService,
                 cache_token: CacheToken):
        self.user_repository = user_repository
        self.cache_otp = cache_otp
        self.token_service = token_service
        self.cache_token = cache_token

    async def execute(self, email: str, otp: str) -> dict[str, str]:
        try:
            otp_data = await self.cache_otp.verify_signup_otp(email=email, otp=otp)

            new_user = UserEntity(
                id=None,
                name=otp_data["name"],
                email=otp_data["email"],
                password=otp_data["password"],
                avatar=None,
                last_login=None,
                status=UserStatus.ACTIVE,
            )

            user = await self.user_repository.create_user(new_user)
            refresh_token, device_id = self.token_service.create_refresh_token(
                user_id=user.id,
                signin_count=user.signin_count,
                sign_out_count=user.sign_out_count
            )
            access_token = self.token_service.create_access_token(
                user_id=user.id,
                signin_count=user.signin_count,
                sign_out_count=user.sign_out_count,
                refresh_jti=device_id
            )

            await self.cache_token.save_refresh_token(
                user_id=user.id,
                device_id=device_id,
                token=refresh_token
            )

            return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "Bearer"}

        except AppError:
            raise

        except Exception as e:
            logger.error(f"SignupVerificationUseCase: {e}")
            raise ServerError() from e
