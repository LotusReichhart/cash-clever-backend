import logging

from src.application.interfaces.cache import CacheToken
from src.domain.exceptions.app_exceptions import ServerError, UnauthorizedError, AppError
from src.application.interfaces.repositories import UserRepository
from src.application.interfaces.services import TokenService

logger = logging.getLogger(__name__)


class RefreshSigninUseCase:
    def __init__(self,
                 user_repository: UserRepository,
                 token_service: TokenService,
                 cache_token: CacheToken):
        self.user_repository = user_repository
        self.token_service = token_service
        self.cache_token = cache_token

    async def execute(self, refresh_token: str) -> dict[str, str]:
        try:
            # Giải mã token
            payload = self.token_service.verify_refresh_token(
                token=refresh_token,
            )

            user_id = payload["id"]
            device_id = payload["jti"]
            signin_count = payload["signin_count"]
            sign_out_count = payload["sign_out_count"]

            # Lấy user trong DB
            user = await self.user_repository.get_user_by_id(user_id=user_id)
            if not user:
                raise UnauthorizedError()

            # Kiểm tra sync giữa token và user (chống reuse)
            if (
                    user.signin_count != signin_count
                    or user.sign_out_count != sign_out_count
            ):
                # Token cũ (user đã đăng nhập lại hoặc đăng xuất sau khi token này phát hành)
                await self.cache_token.delete_all_refresh_tokens(user_id)
                raise UnauthorizedError()

            # Kiểm tra refresh token hash
            stored_hash = await self.cache_token.get_refresh_token_hash(user_id, device_id)
            if not stored_hash or self.cache_token.hash_token(refresh_token) != stored_hash:
                # BREACH DETECTION: refresh token không khớp
                await self.cache_token.delete_all_refresh_tokens(user_id)
                raise UnauthorizedError()

            # Nếu mọi thứ OK → tạo access token mới
            access_token = self.token_service.create_access_token(
                user_id=user.id,
                signin_count=signin_count,
                sign_out_count=sign_out_count,
                refresh_jti=device_id
            )

            return {"access_token": access_token, "token_type": "Bearer"}

        except UnauthorizedError:
            raise

        except AppError:
            raise

        except Exception as e:
            logger.error(f"RefreshSigninUseCase: {e}")
            raise ServerError() from e
