from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.entities.category_entity import CategoryEntity


class CategoryRepository(ABC):

    @abstractmethod
    async def get_paginated_parents(
            self,
            user_id: int,
            search_term: Optional[str],
            limit: int,
            offset: int
    ) -> List[CategoryEntity]:
        pass

    @abstractmethod
    async def get_children_for_parents(
            self,
            parent_ids: List[int]
    ) -> List[CategoryEntity]:
        pass

    @abstractmethod
    async def count_parents(
            self,
            user_id: int,
            search_term: Optional[str]
    ) -> int:
        pass

    @abstractmethod
    async def get_by_id(self, category_id: int, user_id: int) -> Optional[CategoryEntity]:
        pass

    @abstractmethod
    async def get_direct_children(
            self, parent_id: int, user_id: int
    ) -> List[CategoryEntity]:
        pass

    @abstractmethod
    async def create(
            self,
            name: str,
            icon_url: Optional[str],
            user_id: int,
            parent_id: Optional[int]
    ) -> bool:
        pass
