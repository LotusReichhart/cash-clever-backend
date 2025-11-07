import logging

from sqlalchemy import select, func, or_, text
from typing import List, Optional

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import noload

from src.application.interfaces.repositories.category_repository import CategoryRepository
from src.domain.entities.category_entity import CategoryEntity
from src.infrastructure.database.postgresql import SQLAlchemyRepository
from src.infrastructure.database.postgresql.mapper import CategoryMapper
from src.infrastructure.database.postgresql.models import CategoryModel

logger = logging.getLogger(__name__)


class CategoryRepositoryImpl(CategoryRepository, SQLAlchemyRepository):

    def __init__(self, db):
        super().__init__(db, CategoryModel)
        self._mapper = CategoryMapper()

    async def get_paginated_parents(
            self,
            user_id: int,
            search_term: Optional[str],
            limit: int,
            offset: int
    ) -> List[CategoryEntity]:

        base_where = [
            or_(
                CategoryModel.is_system_owned == True,
                CategoryModel.user_id == user_id
            ),
            CategoryModel.parent_id == None
        ]

        if search_term:
            search_query = func.unaccent(f"%{search_term}%")
            base_where.append(
                func.unaccent(CategoryModel.name).ilike(search_query)
            )

        query = (
            select(CategoryModel)
            .options(noload(CategoryModel.children))
            .where(*base_where)
            .order_by(text("unaccent(name)"))  # Sort tiếng Việt
            .limit(limit)
            .offset(offset)
        )

        result = await self.db.execute(query)
        models = result.scalars().all()
        return [self._mapper.to_entity(model) for model in models]

    async def get_children_for_parents(
            self, parent_ids: List[int]
    ) -> List[CategoryEntity]:

        if not parent_ids:
            return []

        query = (
            select(CategoryModel)
            .options(noload(CategoryModel.children))
            .where(CategoryModel.parent_id.in_(parent_ids))
            .order_by(text("unaccent(name)"))
        )

        result = await self.db.execute(query)
        models = result.scalars().all()
        return [self._mapper.to_entity(model) for model in models]

    async def count_parents(
            self,
            user_id: int,
            search_term: Optional[str]
    ) -> int:
        base_where = [
            or_(
                CategoryModel.is_system_owned == True,
                CategoryModel.user_id == user_id
            ),
            CategoryModel.parent_id == None
        ]
        if search_term:
            search_query = func.unaccent(f"%{search_term}%")
            base_where.append(
                func.unaccent(CategoryModel.name).ilike(search_query)
            )
        query = (
            select(func.count(CategoryModel.id))
            .where(*base_where)
        )
        result = await self.db.scalar(query)
        return result or 0

    async def get_by_id(self, category_id: int, user_id: int) -> Optional[CategoryEntity]:
        query = (
            select(CategoryModel)
            .options(
                noload(CategoryModel.children),
                noload(CategoryModel.parent)
            )
            .where(
                CategoryModel.id == category_id,
                or_(
                    CategoryModel.is_system_owned == True,
                    CategoryModel.user_id == user_id
                )
            )
        )

        result = await self.db.execute(query)
        model = result.scalar_one_or_none()

        if model:
            return self._mapper.to_entity(model)

        return None

    async def get_direct_children(
            self, parent_id: int, user_id: int
    ) -> List[CategoryEntity]:
        query = (
            select(CategoryModel)
            .options(
                noload(CategoryModel.children),
                noload(CategoryModel.parent)
            )
            .where(
                CategoryModel.parent_id == parent_id,
                or_(
                    CategoryModel.is_system_owned == True,
                    CategoryModel.user_id == user_id
                )
            )
            .order_by(text("unaccent(name)"))
        )
        result = await self.db.execute(query)
        models = result.scalars().all()
        return [self._mapper.to_entity(model) for model in models]

    async def create(
            self,
            name: str,
            icon_url: Optional[str],
            user_id: int,
            parent_id: Optional[int]
    ) -> bool:

        new_model = self._mapper.to_model_for_create(
            name=name,
            user_id=user_id,
            icon_url=icon_url,
            parent_id=parent_id,
            is_system_owned=False
        )

        try:
            self.db.add(new_model)
            await self.db.commit()

            return True

        except IntegrityError as e:
            logger.warning(f"Lỗi vi phạm ràng buộc DB khi tạo category: {e}")
            await self.db.rollback()
            return False

        except SQLAlchemyError as e:
            logger.error(f"Lỗi SQLAlchemy khi tạo category: {e}")
            await self.db.rollback()
            return False
