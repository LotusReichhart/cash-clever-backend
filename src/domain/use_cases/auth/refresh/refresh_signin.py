import logging

from src.core.config import settings
from src.core.exceptions import ServerError, UnauthorizedError, AppError
from src.domain.repositories import UserRepository
from src.domain.services import TokenService

logger = logging.getLogger(__name__)


class RefreshSigninUseCase:
    def __init__(self,
                 user_repository: UserRepository,
                 token_service: TokenService):
        self.user_repository = user_repository
        self.token_service = token_service

    async def execute(self, refresh_token: str) -> dict[str, str]:
        try:
            # Giải mã token
            payload = self.token_service.verify_token(
                token=refresh_token,
                secret=settings.JWT_REFRESH_SECRET
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
                await self.token_service.delete_all_refresh_tokens(user_id)
                raise UnauthorizedError()

            # Kiểm tra refresh token hash
            stored_hash = await self.token_service.get_refresh_token_hash(user_id, device_id)
            if not stored_hash or self.token_service.hash_token(refresh_token) != stored_hash:
                # BREACH DETECTION: refresh token không khớp
                await self.token_service.delete_all_refresh_tokens(user_id)
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
