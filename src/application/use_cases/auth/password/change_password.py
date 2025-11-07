import logging

from src.application.interfaces.cache import CacheToken
from src.domain.exceptions.app_exceptions import ServerError, AppError, ForbiddenError
from src.domain.exceptions.auth_exception import UserNotFoundError
from src.application.interfaces.repositories import UserRepository
from src.application.interfaces.services import PasswordHasherService

logger = logging.getLogger(__name__)


class ChangePasswordUseCase:
    def __init__(self,
                 user_repository: UserRepository,
                 cache_token: CacheToken,
                 password_hasher_service: PasswordHasherService):
        self.user_repository = user_repository
        self.cache_token = cache_token
        self.password_hasher_service = password_hasher_service

    async def execute(self, reset_token: str, new_password: str):
        token_data = await self.cache_token.verify_reset_token(reset_token)
        if not token_data:
            raise ForbiddenError()

        user_id = token_data["user_id"]

        if not user_id:
            raise ForbiddenError()

        user_id = int(user_id)

        try:
            hashed_pw = self.password_hasher_service.hash(new_password)
            updates = {"password": hashed_pw}
            user = await self.user_repository.update_user_by_id(user_id, updates)
            if not user:
                raise UserNotFoundError()

        except AppError:
            raise

        except Exception as e:
            logger.error(f"ChangePasswordUseCase: {e}")
            raise ServerError() from e
