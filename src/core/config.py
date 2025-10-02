import os

from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Lấy ENV từ biến môi trường, mặc định = development
env = os.getenv("ENV", "development")

# Load file .env.<env>
dotenv_file = f".env.{env}"
load_dotenv(dotenv_file)


class Settings(BaseSettings):
    APP_NAME: str = "Cash Clever Backend"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    class Config:
        env_file = dotenv_file
        env_file_encoding = "utf-8"


settings = Settings()
