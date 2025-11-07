import asyncio
import redis.asyncio as redis

import logging

from src.core.config.settings import settings

logger = logging.getLogger(__name__)

REDIS_URL = (
    f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"
    if not settings.REDIS_USE_TLS
    else f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"
)

redis_client = redis.from_url(
    REDIS_URL,
    password=settings.REDIS_PASSWORD,
    encoding="utf-8",
    decode_responses=True,
)


async def connect_redis(max_retries: int = 20):
    retries = 0
    while retries < max_retries:
        try:
            await redis_client.ping()
            logger.info("Connected to Redis")
            return
        except redis.ConnectionError as e:
            retries += 1
            wait_time = min(retries * 0.1, 3)
            logger.warning(f"Redis reconnect attempt {retries}, retrying in {wait_time}s...")
            await asyncio.sleep(wait_time)
    raise ConnectionError("Redis reconnect failed after 20 attempts")


async def close_redis():
    await redis_client.close()
    logger.info("Redis connection closed")
