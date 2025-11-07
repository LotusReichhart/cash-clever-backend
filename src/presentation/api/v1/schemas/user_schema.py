from pydantic import BaseModel, ConfigDict
from datetime import datetime

from src.domain.entities.user_entity import UserStatus


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    avatar: str | None = None
    last_login: datetime | None = None
    status: UserStatus

    model_config = ConfigDict(from_attributes=True)
