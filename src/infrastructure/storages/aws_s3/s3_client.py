from contextlib import asynccontextmanager
from aiobotocore.session import get_session
from src.core.config.settings import settings # Import settings

@asynccontextmanager
async def get_s3_client():
    session = get_session()
    async with session.create_client(
        's3',
        region_name=settings.AWS_S3_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    ) as client:
        try:
            yield client
        finally:
            pass