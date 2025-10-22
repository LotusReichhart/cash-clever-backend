from dependency_injector import containers, providers

from src.data.cache.redis_service import RedisService
from src.data.services import (
    OTPServiceImpl,
    TokenServiceImpl,
    MailServiceImpl,
    PasswordHasherServiceImpl
)
from src.data.db.session import get_db_session
from src.data.mail.mailer import MailTransporter
from src.data.repositories import UserRepositoryImpl

from src.domain.use_cases.auth import (
    RequestSignupUseCase,
    SignupVerificationUseCase,
    SigninWithEmailPasswordUseCase,
    RequestForgotPasswordUseCase,
    PasswordVerificationUseCase,
    ChangePasswordUseCase,
    ResendOTPUseCase,
    HandleGoogleAuthUseCase,
    RefreshSigninUseCase,
    SignOutAndClearTokenUseCase
)


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=["src.presentation.api.v1"]
    )

    db_session = providers.Resource(get_db_session)

    # Repositories
    user_repository = providers.Factory(UserRepositoryImpl, db=db_session)

    # Services
    # -------------------------- Singleton ------------------------------
    redis_service = providers.Singleton(RedisService)
    mail_transporter = providers.Singleton(MailTransporter)
    # ------------------------- Factory --------------------------
    otp_service = providers.Factory(OTPServiceImpl, redis_service=redis_service)
    token_service = providers.Factory(TokenServiceImpl, redis_service=redis_service)
    mail_service = providers.Factory(MailServiceImpl, transporter=mail_transporter)
    password_hasher_service = providers.Factory(PasswordHasherServiceImpl)
    # ------------------------------------------------------------

    # Use cases

    # Signup
    request_signup_use_case = providers.Factory(
        RequestSignupUseCase,
        user_repository=user_repository,
        otp_service=otp_service,
        mail_service=mail_service,
        password_hasher_service=password_hasher_service
    )
    signup_verification_use_case = providers.Factory(
        SignupVerificationUseCase,
        user_repository=user_repository,
        otp_service=otp_service,
        token_service=token_service
    )

    # Signin
    signin_with_email_password_use_case = providers.Factory(
        SigninWithEmailPasswordUseCase,
        user_repository=user_repository,
        password_hasher_service=password_hasher_service,
        token_service=token_service
    )

    # OTPs
    resend_otp_use_case = providers.Factory(
        ResendOTPUseCase,
        otp_service=otp_service,
        mail_service=mail_service
    )

    # Forgot Password
    request_forgot_password_use_case = providers.Factory(
        RequestForgotPasswordUseCase,
        user_repository=user_repository,
        otp_service=otp_service,
        mail_service=mail_service
    )
    password_verification_use_case = providers.Factory(
        PasswordVerificationUseCase,
        otp_service=otp_service,
        token_service=token_service
    )
    change_password_use_case = providers.Factory(
        ChangePasswordUseCase,
        user_repository=user_repository,
        token_service=token_service,
        password_hasher_service=password_hasher_service
    )

    # Refresh
    refresh_signin_use_case = providers.Factory(
        RefreshSigninUseCase,
        user_repository=user_repository,
        token_service=token_service
    )

    # Sign Out
    sign_out_and_clear_token_use_case = providers.Factory(
        SignOutAndClearTokenUseCase,
        user_repository=user_repository,
        token_service=token_service
    )

    # Google Auth
    handle_google_auth_use_case = providers.Factory(
        HandleGoogleAuthUseCase,
        user_repository=user_repository,
        token_service=token_service
    )
