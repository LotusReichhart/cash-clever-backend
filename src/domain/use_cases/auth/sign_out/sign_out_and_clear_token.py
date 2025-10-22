import logging

from src.core.exceptions import ServerError, UnauthorizedError, AppError
from src.domain.exceptions.auth_exception import EmailNotRegisteredError
from src.domain.repositories import UserRepository
from src.domain.services import TokenService

logger = logging.getLogger(__name__)


class SignOutAndClearTokenUseCase:
    def __init__(self,
                 user_repository: UserRepository,
                 token_service: TokenService):
        self.user_repository = user_repository
        self.token_service = token_service

    async def execute(self, user_id: int, signin_count: int, sign_out_count: int):
        user = await self.user_repository.get_user_by_id(user_id=user_id)

        if not user:
            raise EmailNotRegisteredError()

        if (
                user.signin_count != signin_count
                or user.sign_out_count != sign_out_count
        ):
            # Token cũ (user đã đăng nhập lại hoặc đăng xuất sau khi token này phát hành)
            await self.token_service.delete_all_refresh_tokens(user_id)
            raise UnauthorizedError()

        try:
            user.increase_sign_out_count()
            updates = {"sign_out_count": user.sign_out_count}

            await self.user_repository.update_user_by_id(user.id, updates)

            await self.token_service.delete_all_refresh_tokens(user_id=user.id)

        except AppError:
            raise

        except Exception as e:
            logger.error(f"SignOutAndClearTokenUseCase {e}")
            raise ServerError() from e
