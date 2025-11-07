import logging
from typing import List, Dict, Optional

from src.domain.entities import CategoryEntity
from src.application.interfaces.repositories import CategoryRepository

from src.domain.exceptions.app_exceptions import AppError, ServerError

logger = logging.getLogger(__name__)


class GetCategoryTreeUseCase:
    def __init__(self,
                 category_repository: CategoryRepository):
        self._category_repository = category_repository

    async def execute(
            self,
            user_id: int,
            limit: int,
            offset: int,
            search_term: Optional[str] = None,
    ) -> dict:
        try:
            total_parents = await self._category_repository.count_parents(
                user_id, search_term
            )
            if total_parents == 0:
                return {"categories": [], "has_more": False}

            # 1. Lấy Entities cha (đã sort)
            parent_entities = await self._category_repository.get_paginated_parents(
                user_id=user_id,
                search_term=search_term,
                limit=limit,
                offset=offset
            )
            if not parent_entities:
                return {"categories": [], "has_more": False}

            # 2. Lấy Entities con
            parent_ids = [p.id for p in parent_entities]
            children_entities = await self._category_repository.get_children_for_parents(
                parent_ids=parent_ids
            )

            all_items_map: Dict[int, CategoryEntity] = {
                entity.id: entity for entity in (parent_entities + children_entities)
            }

            final_tree: List[CategoryEntity] = []
            for entity in all_items_map.values():
                if entity.parent_id:
                    parent = all_items_map.get(entity.parent_id)
                    if parent:
                        parent.children.append(entity)
                else:
                    final_tree.append(entity)

            has_more = (offset + len(parent_entities)) < total_parents

            final_tree_as_dict = [
                entity.model_dump(mode='json') for entity in final_tree
            ]

            return {"categories": final_tree_as_dict, "has_more": has_more}

        except AppError:
            raise

        except Exception as e:
            logger.error(f"GetCategoryTreeUseCase error: {e}")
            raise ServerError() from e
