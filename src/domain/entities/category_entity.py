from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, ConfigDict


class CategoryStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BANNED = "banned"


class CategoryEntity(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    icon_url: Optional[str] = None
    is_system_owned: bool
    status: CategoryStatus
    parent_id: Optional[int] = None
    user_id: Optional[int] = None

    # Dùng cho việc build cây
    children: List['CategoryEntity'] = []


# Cập nhật tham chiếu đệ quy
CategoryEntity.model_rebuild()
