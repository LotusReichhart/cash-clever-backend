from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError

from src.domain.exceptions.app_exceptions import ServerError
from src.infrastructure.database.postgresql.mapper import UserMapper

from src.infrastructure.database.postgresql.models import UserModel
from src.infrastructure.database.postgresql.sql_al_chemy_repository import SQLAlchemyRepository

from src.domain.entities import UserEntity
from src.application.interfaces.repositories import UserRepository


class UserRepositoryImpl(UserRepository, SQLAlchemyRepository):
    def __init__(self, db):
        super().__init__(db, UserModel)

    async def create_user(self, user: UserEntity) -> UserEntity:
        user_model = UserMapper.to_user_model(user)

        self.db.add(user_model)

        try:
            await self.safe_commit()
            await self.db.refresh(user_model)
            return UserMapper.to_user_entity(user_model)
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise ServerError(detail=str(e)) from e

    async def exists_by_email(self, email: str) -> bool:
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_user_by_id(self, user_id: int) -> UserEntity | None:
        try:
            stmt = select(UserModel).where(UserModel.id == user_id)
            result = await self.db.execute(stmt)
            user_model = result.scalar_one_or_none()

            if not user_model:
                return None

            return UserMapper.to_user_entity(user_model)
        except SQLAlchemyError as e:
            raise ServerError(detail=str(e)) from e

    async def get_user_by_email(self, email: str) -> UserEntity | None:
        try:
            stmt = select(UserModel).where(UserModel.email == email)
            result = await self.db.execute(stmt)
            user_model = result.scalar_one_or_none()

            if not user_model:
                return None

            return UserMapper.to_user_entity(user_model)
        except SQLAlchemyError as e:
            raise ServerError(detail=str(e)) from e

    async def update_user_by_id(self, user_id: int, updates: dict) -> UserEntity | None:
        """
        Cập nhật thông tin user theo ID.
        :param user_id: int - ID của user cần cập nhật
        :param updates: dict - Các trường cần cập nhật (ví dụ: {"name": "New Name"})
        :return: User domain object hoặc None nếu không tìm thấy user
        """
        try:
            stmt = (
                update(UserModel)
                .where(UserModel.id == user_id)
                .values(**updates)
                .returning(UserModel)
            )
            result = await self.db.execute(stmt)
            user_model = result.scalar_one_or_none()

            if not user_model:
                return None

            await self.safe_commit()
            return UserMapper.to_user_entity(user_model)

        except SQLAlchemyError as e:
            await self.db.rollback()
            raise ServerError(detail=str(e)) from e

