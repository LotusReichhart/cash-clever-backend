import pytest
from unittest.mock import AsyncMock, MagicMock
from src.domain.exceptions.auth_exception import EmailAlreadyUsedError, TooManyOtpRequestsError
from src.application.use_cases.auth.signup.request_signup import RequestSignupUseCase
from src.domain.exceptions.app_exceptions import ServerError


@pytest.mark.asyncio
class TestRequestSignupUseCase:
    async def test_successful_signup(self):
        # Mocks
        user_repo = AsyncMock()
        user_repo.exists_by_email = AsyncMock(return_value=False)

        otp_service = AsyncMock()
        otp_service.check_and_increment_limit = AsyncMock(return_value=True)
        otp_service.generate_otp = MagicMock(return_value="123456")
        otp_service.save_signup_otp = AsyncMock()

        mail_service = AsyncMock()
        mail_service.build_otp_template = MagicMock(return_value={
            "subject": "Test Subject",
            "html": "<p>Test HTML</p>",
        })
        mail_service.send_mail = AsyncMock()

        password_hasher = MagicMock()
        password_hasher.hash.return_value = "hashed_pw"

        # Instantiate use case
        use_case = RequestSignupUseCase(
            user_repository=user_repo,
            otp_service=otp_service,
            mail_service=mail_service,
            password_hasher_service=password_hasher,
        )

        # Run
        result = await use_case.execute("test@example.com", "Test User", "123456")

        # Assert
        assert result == {"email": "test@example.com"}
        otp_service.save_signup_otp.assert_awaited_once_with(
            email="test@example.com",
            otp="123456",
            name="Test User",
            password="hashed_pw",
        )
        mail_service.send_mail.assert_awaited_once()
        password_hasher.hash.assert_called_once_with("123456")

    async def test_existing_user_raises_email_already_used_error(self):
        user_repo = AsyncMock()
        user_repo.exists_by_email = AsyncMock(return_value=True)

        otp_service = AsyncMock()
        mail_service = AsyncMock()
        password_hasher = MagicMock()

        use_case = RequestSignupUseCase(
            user_repository=user_repo,
            otp_service=otp_service,
            mail_service=mail_service,
            password_hasher_service=password_hasher,
        )

        with pytest.raises(EmailAlreadyUsedError):
            await use_case.execute("used@example.com", "User", "pw")

    async def test_too_many_otp_requests(self):
        user_repo = AsyncMock()
        user_repo.exists_by_email = AsyncMock(return_value=False)

        otp_service = AsyncMock()
        otp_service.check_and_increment_limit = AsyncMock(return_value=False)

        mail_service = AsyncMock()
        password_hasher = MagicMock()

        use_case = RequestSignupUseCase(
            user_repository=user_repo,
            otp_service=otp_service,
            mail_service=mail_service,
            password_hasher_service=password_hasher,
        )

        with pytest.raises(TooManyOtpRequestsError):
            await use_case.execute("limit@example.com", "Limit", "pw")

    async def test_unexpected_error_raises_server_error(self):
        user_repo = AsyncMock()
        user_repo.exists_by_email = AsyncMock(return_value=False)

        otp_service = AsyncMock()
        otp_service.check_and_increment_limit = AsyncMock(side_effect=RuntimeError("Something broke"))

        mail_service = AsyncMock()
        password_hasher = MagicMock()

        use_case = RequestSignupUseCase(
            user_repository=user_repo,
            otp_service=otp_service,
            mail_service=mail_service,
            password_hasher_service=password_hasher,
        )

        with pytest.raises(ServerError):
            await use_case.execute("test@example.com", "User", "pw")
