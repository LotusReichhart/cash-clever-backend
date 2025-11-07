import logging
from typing import Optional

from src.application.interfaces.repositories import CategoryRepository
from src.domain.exceptions.app_exceptions import AppError, ServerError

logger = logging.getLogger(__name__)


class CreateCategoryUseCase:

    def __init__(self,
                 category_repository: CategoryRepository):
        self._category_repository = category_repository

    async def execute(
            self,
            name: str,
            user_id: int,
            parent_id: Optional[int],
            icon_url: Optional[str]
    ):
        try:
            await self._category_repository.create(
                name=name,
                user_id=user_id,
                parent_id=parent_id,
                icon_url=icon_url
            )

        except AppError:
            raise
        except Exception as e:
            logger.error(f"CreateCategoryUseCase error: {e}")
            raise ServerError()
