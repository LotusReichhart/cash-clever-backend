from typing import Optional

from src.domain.entities import CategoryEntity, CategoryStatus
from src.infrastructure.database.postgresql.models import CategoryModel


class CategoryMapper:
    @staticmethod
    def to_entity(model: CategoryModel) -> CategoryEntity:
        """Chuyển Model (DB) sang Entity (Domain)"""
        # Pydantic's model_validate sẽ tự động map các trường
        return CategoryEntity.model_validate(model)

    @staticmethod
    def to_model_for_create(
            name: str,
            user_id: int,
            parent_id: Optional[int],
            is_system_owned: bool,
            icon_url: Optional[str] = None,
    ) -> CategoryModel:
        """Chuyển dữ liệu đầu vào sang Model (DB) để tạo mới"""
        return CategoryModel(
            name=name,
            icon_url=icon_url,
            user_id=user_id,
            parent_id=parent_id,
            is_system_owned=is_system_owned,
            status=CategoryStatus.ACTIVE
        )
