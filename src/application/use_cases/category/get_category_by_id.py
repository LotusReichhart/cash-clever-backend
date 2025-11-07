import logging

from src.application.interfaces.repositories import CategoryRepository

from src.domain.exceptions.app_exceptions import AppError, ServerError

logger = logging.getLogger(__name__)


class GetCategoryByIdUseCase:
    def __init__(self,
                 category_repository: CategoryRepository):
        self._category_repository = category_repository

    async def execute(
            self,
            category_id: int,
            user_id: int,
    ) -> dict:
        try:
            category = await self._category_repository.get_by_id(
                category_id=category_id, user_id=user_id
            )

            if not category:
                return {"category": None}

            parent_entity = None

            if category.parent_id:
                parent_entity = await self._category_repository.get_by_id(
                    category_id=category.parent_id, user_id=user_id
                )

            children_entities = await self._category_repository.get_direct_children(
                parent_id=category.id, user_id=user_id
            )

            children_list_dict = [
                child.model_dump(mode='json') for child in children_entities
            ]

            category.children = children_list_dict

            category_as_dict = category.model_dump(mode='json')
            parent_as_dict = parent_entity.model_dump(mode='json') if parent_entity else None

            return {"category": category_as_dict, "parent": parent_as_dict}

        except AppError:
            raise

        except Exception as e:
            logger.error(f"GetCategoryByIdUseCase error: {e}")
            raise ServerError() from e
