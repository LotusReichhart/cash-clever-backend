import pytest
import logging
from unittest.mock import AsyncMock, MagicMock

from src.core.exceptions import ServerError, AppError
from src.domain.entities import UserEntity
from src.domain.exceptions.auth_exception import EmailNotRegisteredError, IncorrectPasswordError
from src.domain.use_cases.auth import SigninWithEmailPasswordUseCase


@pytest.mark.asyncio
class TestSigninWithEmailPasswordUseCase:

    async def test_email_not_registered_raises_error(self):
        user_repo = AsyncMock()
        password_hasher = MagicMock()
        token_service = MagicMock()

        user_repo.get_user_by_email = AsyncMock(return_value=None)

        use_case = SigninWithEmailPasswordUseCase(
            user_repository=user_repo,
            password_hasher_service=password_hasher,
            token_service=token_service
        )

        with pytest.raises(EmailNotRegisteredError):
            await use_case.execute("test@example.com", "123456")

    async def test_incorrect_password_raises_error(self):
        user_repo = AsyncMock()
        password_hasher = MagicMock()
        token_service = MagicMock()

        fake_user = MagicMock()
        fake_user.password = "hashed_pw"
        user_repo.get_user_by_email = AsyncMock(return_value=fake_user)
        password_hasher.verify.return_value = False

        use_case = SigninWithEmailPasswordUseCase(
            user_repository=user_repo,
            password_hasher_service=password_hasher,
            token_service=token_service
        )

        with pytest.raises(IncorrectPasswordError):
            await use_case.execute("test@example.com", "wrong")

    async def test_successful_signin_returns_tokens(self):
        user_repo = AsyncMock()
        password_hasher = MagicMock()
        token_service = MagicMock()

        fake_user = MagicMock()
        fake_user.id = 1
        fake_user.password = "hashed_pw"
        fake_user.signin_count = 0
        fake_user.sign_out_count = 0
        fake_user.increase_signin_count = MagicMock(side_effect=lambda: setattr(fake_user, "signin_count", 1))

        user_repo.get_user_by_email = AsyncMock(return_value=fake_user)
        user_repo.update_user_by_id = AsyncMock()

        password_hasher.verify.return_value = True

        token_service.create_refresh_token.return_value = ("refresh123", "device123")
        token_service.create_access_token.return_value = "access123"

        use_case = SigninWithEmailPasswordUseCase(
            user_repository=user_repo,
            password_hasher_service=password_hasher,
            token_service=token_service
        )

        result = await use_case.execute("test@example.com", "123456")

        assert result == {
            "access_token": "access123",
            "refresh_token": "refresh123",
            "token_type": "Bearer"
        }
        user_repo.update_user_by_id.assert_awaited_once_with(1, {"signin_count": 1})

    async def test_app_error_propagates(self):
        user_repo = AsyncMock()
        password_hasher = MagicMock()
        token_service = MagicMock()

        fake_user = MagicMock()
        fake_user.id = 1
        fake_user.password = "hashed_pw"
        fake_user.signin_count = 0
        fake_user.sign_out_count = 0
        fake_user.increase_signin_count = MagicMock(side_effect=lambda: setattr(fake_user, "signin_count", 1))

        user_repo.get_user_by_email = AsyncMock(return_value=fake_user)
        user_repo.update_user_by_id = AsyncMock(side_effect=AppError("db error"))
        password_hasher.verify.return_value = True

        use_case = SigninWithEmailPasswordUseCase(
            user_repository=user_repo,
            password_hasher_service=password_hasher,
            token_service=token_service
        )

        with pytest.raises(AppError):
            await use_case.execute("test@example.com", "123456")

    async def test_unexpected_error_raises_server_error(self):
        user_repo = AsyncMock()
        password_hasher = MagicMock()
        token_service = MagicMock()

        fake_user = MagicMock()
        fake_user.password = "hashed_pw"
        fake_user.increase_signin_count = MagicMock()

        user_repo.get_user_by_email = AsyncMock(return_value=fake_user)
        password_hasher.verify.return_value = True

        user_repo.update_user_by_id = AsyncMock(side_effect=RuntimeError("DB crash"))

        use_case = SigninWithEmailPasswordUseCase(
            user_repository=user_repo,
            password_hasher_service=password_hasher,
            token_service=token_service
        )

        with pytest.raises(ServerError):
            await use_case.execute("test@example.com", "123456")
