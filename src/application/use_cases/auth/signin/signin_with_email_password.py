import logging

from src.application.interfaces.cache import CacheToken
from src.domain.exceptions.app_exceptions import ServerError, AppError
from src.domain.exceptions.auth_exception import EmailNotRegisteredError, IncorrectPasswordError
from src.application.interfaces.repositories.user_repository import UserRepository
from src.application.interfaces.services import PasswordHasherService, TokenService

logger = logging.getLogger(__name__)


class SigninWithEmailPasswordUseCase:
    def __init__(self,
                 user_repository: UserRepository,
                 password_hasher_service: PasswordHasherService,
                 token_service: TokenService,
                 cache_token: CacheToken):
        self.user_repository = user_repository
        self.password_hasher_service = password_hasher_service
        self.token_service = token_service
        self.cache_token = cache_token

    async def execute(self, email: str, password: str) -> dict[str, str]:

        user = await self.user_repository.get_user_by_email(email)

        if not user:
            raise EmailNotRegisteredError()

        is_verify = self.password_hasher_service.verify(hashed_password=user.password, password=password)

        if not is_verify:
            raise IncorrectPasswordError()

        try:
            user.increase_signin_count()

            updates = {"signin_count": user.signin_count}

            await self.user_repository.update_user_by_id(user.id, updates)

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

            return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "Bearer"}

        except AppError:
            raise

        except Exception as e:
            logger.error(f"SigninWithEmailPasswordUseCase: {e}")
            raise ServerError() from e
