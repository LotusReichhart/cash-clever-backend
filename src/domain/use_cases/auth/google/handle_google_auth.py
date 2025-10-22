import logging

from google.oauth2 import id_token
from google.auth.transport import requests

from src.core.config import settings
from src.core.exceptions import ServerError, AppError
from src.domain.entities.user_entity import UserStatus, UserEntity
from src.domain.repositories import UserRepository
from src.domain.services import TokenService

logger = logging.getLogger(__name__)


class HandleGoogleAuthUseCase:
    def __init__(self,
                 user_repository: UserRepository,
                 token_service: TokenService):
        self.user_repository = user_repository
        self.token_service = token_service
        self.client_id = settings.GOOGLE_CLIENT_ID

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

            await self.token_service.save_refresh_token(
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
