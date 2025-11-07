from dataclasses import field
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BANNED = "banned"


class UserEntity(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    name: str
    email: str
    password: Optional[str] = None
    avatar: Optional[str] = None
    last_login: datetime | None
    signin_count: int = field(default=0)
    sign_out_count: int = field(default=0)
    status: UserStatus = UserStatus.ACTIVE

    def increase_signin_count(self):
        """Tăng số lần đăng nhập của user."""
        self.signin_count += 1

    def increase_sign_out_count(self):
        """Tăng số lần đăng xuất chủ động của user."""
        self.sign_out_count += 1
