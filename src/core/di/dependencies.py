from dependency_injector import containers, providers

from src.application.use_cases.category.create_category import CreateCategoryUseCase
from src.application.use_cases.category.get_category_by_id import GetCategoryByIdUseCase
from src.application.use_cases.category.get_category_tree import GetCategoryTreeUseCase
from src.application.use_cases.images.get_list_images import GetListImagesUseCase
from src.application.use_cases.images.upload_image import UploadImageUseCase
from src.core.config.settings import settings

from src.application.use_cases.auth.google.handle_google_auth import HandleGoogleAuthUseCase
from src.application.use_cases.auth.otp.resend_otp import ResendOTPUseCase
from src.application.use_cases.auth.password.change_password import ChangePasswordUseCase
from src.application.use_cases.auth.password.password_verification import PasswordVerificationUseCase
from src.application.use_cases.auth.password.request_forgot_password import RequestForgotPasswordUseCase
from src.application.use_cases.auth.refresh.refresh_signin import RefreshSigninUseCase
from src.application.use_cases.auth.sign_out.sign_out_and_clear_token import SignOutAndClearTokenUseCase
from src.application.use_cases.auth.signin.signin_with_email_password import SigninWithEmailPasswordUseCase
from src.application.use_cases.auth.signup.request_signup import RequestSignupUseCase
from src.application.use_cases.auth.signup.signup_verification import SignupVerificationUseCase

from src.infrastructure.cache.redis import (
    RedisMethod, RedisCacheOtp, RedisCacheToken
)
from src.infrastructure.database.postgresql.repositories import (
    UserRepositoryImpl, CategoryRepositoryImpl
)

from src.infrastructure.database.postgresql import get_db_session
from src.infrastructure.external_services.adapters import MailServiceImpl
from src.infrastructure.external_services.mailer import MailTransporter
from src.infrastructure.security import (
    GenerateOtpImpl, JWTTokenService, Argon2PasswordHasher
)
from src.infrastructure.storages.aws_s3 import get_s3_client, S3StorageService


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=["src.presentation.api.v1"]
    )

    db_session = providers.Resource(get_db_session)
    s3_client = providers.Resource(get_s3_client)

    # Repositories
    user_repository = providers.Factory(UserRepositoryImpl, db=db_session)
    category_repository = providers.Factory(CategoryRepositoryImpl, db=db_session)

    # Services
    # -------------------------- Singleton ------------------------------
    redis_method = providers.Singleton(RedisMethod)
    mail_transporter = providers.Singleton(MailTransporter)
    # ------------------------- Factory --------------------------
    generate_otp_service = providers.Factory(GenerateOtpImpl)
    cache_otp = providers.Factory(RedisCacheOtp, redis_method=redis_method)
    token_service = providers.Factory(JWTTokenService)
    cache_token = providers.Factory(RedisCacheToken, redis_method=redis_method)
    mail_service = providers.Factory(MailServiceImpl, transporter=mail_transporter)
    password_hasher_service = providers.Factory(Argon2PasswordHasher)
    storage_service = providers.Factory(S3StorageService, client=s3_client)
    # ------------------------------------------------------------

    # Use cases

    # -----------------------------Auth---------------------------

    # Signup
    request_signup_use_case = providers.Factory(
        RequestSignupUseCase,
        user_repository=user_repository,
        generate_otp_service=generate_otp_service,
        cache_otp=cache_otp,
        mail_service=mail_service,
        password_hasher_service=password_hasher_service
    )
    signup_verification_use_case = providers.Factory(
        SignupVerificationUseCase,
        user_repository=user_repository,
        cache_otp=cache_otp,
        token_service=token_service,
        cache_token=cache_token
    )

    # Signin
    signin_with_email_password_use_case = providers.Factory(
        SigninWithEmailPasswordUseCase,
        user_repository=user_repository,
        password_hasher_service=password_hasher_service,
        token_service=token_service,
        cache_token=cache_token
    )

    # OTPs
    resend_otp_use_case = providers.Factory(
        ResendOTPUseCase,
        generate_otp_service=generate_otp_service,
        cache_otp=cache_otp,
        mail_service=mail_service
    )

    # Forgot Password
    request_forgot_password_use_case = providers.Factory(
        RequestForgotPasswordUseCase,
        user_repository=user_repository,
        generate_otp_service=generate_otp_service,
        cache_otp=cache_otp,
        mail_service=mail_service
    )
    password_verification_use_case = providers.Factory(
        PasswordVerificationUseCase,
        token_service=token_service,
        cache_otp=cache_otp,
        cache_token=cache_token
    )
    change_password_use_case = providers.Factory(
        ChangePasswordUseCase,
        user_repository=user_repository,
        cache_token=cache_token,
        password_hasher_service=password_hasher_service
    )

    # Refresh
    refresh_signin_use_case = providers.Factory(
        RefreshSigninUseCase,
        user_repository=user_repository,
        token_service=token_service,
        cache_token=cache_token
    )

    # Sign Out
    sign_out_and_clear_token_use_case = providers.Factory(
        SignOutAndClearTokenUseCase,
        user_repository=user_repository,
        cache_token=cache_token
    )

    # Google Auth
    handle_google_auth_use_case = providers.Factory(
        HandleGoogleAuthUseCase,
        user_repository=user_repository,
        token_service=token_service,
        cache_token=cache_token,
        client_id=settings.GOOGLE_CLIENT_ID
    )
    # ------------------------------------------------------------

    # -----------------------------Category---------------------------
    get_category_tree_use_case = providers.Factory(
        GetCategoryTreeUseCase,
        category_repository=category_repository
    )
    get_category_by_id_use_case = providers.Factory(
        GetCategoryByIdUseCase,
        category_repository=category_repository
    )
    create_category_use_case = providers.Factory(
        CreateCategoryUseCase,
        category_repository=category_repository
    )

    # -----------------------------Images---------------------------
    upload_image_use_case = providers.Factory(
        UploadImageUseCase,
        storage_service=storage_service
    )
    get_list_images_use_case = providers.Factory(
        GetListImagesUseCase,
        storage_service=storage_service
    )
