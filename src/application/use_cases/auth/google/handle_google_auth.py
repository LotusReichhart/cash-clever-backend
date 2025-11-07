import logging

from google.oauth2 import id_token
from google.auth.transport import requests

from src.application.interfaces.cache import CacheToken
from src.application.interfaces.services import TokenService
from src.domain.exceptions.app_exceptions import ServerError, AppError
from src.domain.entities.user_entity import UserStatus, UserEntity
from src.application.interfaces.repositories import UserRepository

logger = logging.getLogger(__name__)


class HandleGoogleAuthUseCase:
    def __init__(self,
                 user_repository: UserRepository,
                 token_service: TokenService,
                 cache_token: CacheToken,
                 client_id: str):
        self.user_repository = user_repository
        self.token_service = token_service
        self.cache_token = cache_token
        self.client_id = client_id

    async def execute(self, user_id_token: str) -> dict[str, str]:
        try:
            idinfo = id_token.verify_oauth2_token(
                user_id_token, requests.Request(), self.client_id
            )

            user_email = idinfo.get("email")
            if not user_email:
                raise ServerError()

            user = await self.user_repository.get_user_by_email(email=user_email)
            if not user:
                new_user = UserEntity(
                    id=None,
                    name=idinfo.get("name"),
                    email=user_email,
                    password=None,
                    avatar=idinfo.get("picture"),
                    last_login=None,
                    status=UserStatus.ACTIVE,
                )

                try:
                    user = await self.user_repository.create_user(new_user)
                except Exception as e:
                    logger.error(f"HandleGoogleAuthUseCase - create user: {e}")
                    raise ServerError() from e

            refresh_token_data = self.token_service.create_refresh_token(
                user_id=user.id,
                signin_count=user.signin_count,
                sign_out_count=user.sign_out_count
            )
            refresh_token = refresh_token_data["token"]
            device_id = refresh_token_data["device_id"]

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
            logger.error(f"HandleGoogleAuthUseCase: {e}")
            raise ServerError() from e
