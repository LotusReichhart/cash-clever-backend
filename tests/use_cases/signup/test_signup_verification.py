import pytest
from unittest.mock import AsyncMock, MagicMock
from src.application.use_cases.auth.signup.signup_verification import SignupVerificationUseCase
from src.domain.entities import UserEntity, UserStatus
from src.domain.exceptions.app_exceptions import AppError, ServerError


@pytest.mark.asyncio
class TestSignupVerificationUseCase:
    async def test_successful_verification(self):
        # --- Mocks setup ---
        user_repo = AsyncMock()
        otp_service = AsyncMock()
        token_service = MagicMock()
        token_service.save_refresh_token = AsyncMock()

        otp_service.verify_signup_otp.return_value = {
            "email": "test@example.com",
            "name": "Tester",
            "password": "hashed_pw",
        }

        mock_user = UserEntity(
            id=1,
            name="Tester",
            email="test@example.com",
            password="hashed_pw",
            avatar=None,
            last_login=None,
            status=UserStatus.ACTIVE,
        )
        mock_user.signin_count = 1
        mock_user.sign_out_count = 0
        user_repo.create_user.return_value = mock_user

        token_service.create_refresh_token.return_value = ("refresh123", "device123")
        token_service.create_access_token.return_value = "access123"

        # --- Use case ---
        use_case = SignupVerificationUseCase(
            user_repository=user_repo,
            otp_service=otp_service,
            token_service=token_service,
        )

        result = await use_case.execute("test@example.com", "654321")

        # --- Assertions ---
        otp_service.verify_signup_otp.assert_awaited_once_with(email="test@example.com", otp="654321")
        user_repo.create_user.assert_awaited_once()
        token_service.create_refresh_token.assert_called_once_with(
            user_id=1, signin_count=1, sign_out_count=0
        )
        token_service.create_access_token.assert_called_once_with(
            user_id=1, signin_count=1, sign_out_count=0, refresh_jti="device123"
        )
        token_service.save_refresh_token.assert_awaited_once_with(
            user_id=1, device_id="device123", token="refresh123"
        )

        assert result == {
            "access_token": "access123",
            "refresh_token": "refresh123",
            "token_type": "Bearer"
        }

    async def test_app_error_propagates(self):
        user_repo = AsyncMock()
        otp_service = AsyncMock()
        token_service = MagicMock()
        token_service.save_refresh_token = AsyncMock()

        otp_service.verify_signup_otp.return_value = {
            "email": "test@example.com",
            "name": "Tester",
            "password": "hashed_pw",
        }

        user_repo.create_user.side_effect = AppError("Some App Error")

        use_case = SignupVerificationUseCase(
            user_repository=user_repo,
            otp_service=otp_service,
            token_service=token_service,
        )

        with pytest.raises(AppError):
            await use_case.execute("test@example.com", "654321")

    async def test_unexpected_error_raises_server_error(self):
        user_repo = AsyncMock()
        otp_service = AsyncMock()
        token_service = MagicMock()
        token_service.save_refresh_token = AsyncMock()

        otp_service.verify_signup_otp = AsyncMock(side_effect=RuntimeError("DB crash"))

        use_case = SignupVerificationUseCase(
            user_repository=user_repo,
            otp_service=otp_service,
            token_service=token_service,
        )

        with pytest.raises(ServerError):
            await use_case.execute("test@example.com", "654321")
