import logging
from typing import Type, TypeVar, Optional, Any
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

logger = logging.getLogger(__name__)

T = TypeVar("T")


class SQLAlchemyRepository:
    def __init__(self, db: AsyncSession, model: Type[T]):
        """
        Base class for all repositories (Async version).
        :param db: SQLAlchemy AsyncSession
        :param model: SQLAlchemy model class
        """
        self.db = db
        self.model = model

    # ---------- Transaction ----------
    async def safe_commit(self):
        """Commit safely and rollback on failure."""
        try:
            await self.db.commit()
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.exception(f"Database commit failed: {e}")
            raise

    async def rollback(self):
        """Rollback current transaction."""
        await self.db.rollback()

    # ---------- Basic CRUD ----------
    async def add(self, obj: T) -> T:
        """Add an object to the session and commit."""
        self.db.add(obj)
        await self.safe_commit()
        await self.db.refresh(obj)
        return obj

    async def get_by_id(self, obj_id: Any) -> Optional[T]:
        """Return object by primary key, or None."""
        try:
            result = await self.db.get(self.model, obj_id)
            return result
        except SQLAlchemyError as e:
            logger.error(f"Error fetching {self.model.__name__} with id={obj_id}: {e}")
            return None

    async def get_or_none(self, **filters) -> Optional[T]:
        """Return first matching record or None."""
        try:
            stmt = select(self.model).filter_by(**filters)
            result = await self.db.execute(stmt)
            return result.scalars().first()
        except SQLAlchemyError as e:
            logger.error(f"Error filtering {self.model.__name__} with {filters}: {e}")
            return None

    async def delete(self, obj: T):
        """Delete an object and commit."""
        try:
            await self.db.delete(obj)
            await self.safe_commit()
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.exception(f"Delete failed for {self.model.__name__}: {e}")
            raise

    async def update(self, obj: T, **fields):
        """Update fields on an existing object and commit."""
        for key, value in fields.items():
            setattr(obj, key, value)
        try:
            await self.safe_commit()
            await self.db.refresh(obj)
            return obj
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.exception(f"Update failed for {self.model.__name__}: {e}")
            raise
