from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.data.cache.redis_client import connect_redis, close_redis
from src.data.db.base import Base
from src.data.db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating tables (startup)...")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("Connect Redis (startup)...")
    await connect_redis()

    yield

    print("Disconnect Redis (shutdown)...")
    await close_redis()

    print("Shutting down...")
