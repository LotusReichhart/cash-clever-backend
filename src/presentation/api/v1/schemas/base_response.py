from pydantic import BaseModel, ConfigDict
from typing import Generic, TypeVar

T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    model_config = ConfigDict(from_attributes=True)

    status: int
    message: str
    data: T | None
