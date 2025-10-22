import os

from datetime import timedelta
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from dotenv import load_dotenv
from typing import ClassVar

# Lấy ENV từ biến môi trường, mặc định = development
ENV = os.getenv("ENV", "development")

# Load file .env.<env>
dotenv_file = f".env.{ENV}"
load_dotenv(dotenv_file)


class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str
    DEBUG: bool

    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str
    REDIS_USE_TLS: bool = True

    MAIL_HOST: str
    MAIL_PORT: int
    MAIL_USER: str
    MAIL_PASSWORD: str
    MAIL_SENDER_NAME: str

    JWT_ACCESS_SECRET: str
    JWT_REFRESH_SECRET: str

    ACCESS_TOKEN_LIFETIME: ClassVar[timedelta] = timedelta(minutes=30)
    REFRESH_TOKEN_LIFETIME: ClassVar[timedelta] = timedelta(days=45)

    GOOGLE_CLIENT_ID: str

    SESSION_SECRET: str

    model_config = ConfigDict(
        env_file=dotenv_file,
        env_file_encoding="utf-8"
    )


settings = Settings()
