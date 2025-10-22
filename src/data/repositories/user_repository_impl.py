from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError

from src.core.exceptions import ServerError

from src.data.models import UserModel
from src.data.repositories.base_repository import BaseRepository

from src.domain.entities import UserEntity, UserStatus
from src.domain.repositories import UserRepository


class UserRepositoryImpl(UserRepository, BaseRepository):
    def __init__(self, db):
        super().__init__(db, UserModel)

    async def create_user(self, user: UserEntity) -> UserEntity:
        user_model = UserModel(
            name=user.name,
            email=user.email,
            password=user.password,
            avatar=user.avatar,
            last_login=user.last_login,
            signin_count=user.signin_count,
            sign_out_count=user.sign_out_count,
            status=user.status or UserStatus.ACTIVE,
        )

        self.db.add(user_model)

        try:
            await self.safe_commit()
            await self.db.refresh(user_model)
            return self._to_domain(user_model)
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

            return self._to_domain(user_model)
        except SQLAlchemyError as e:
            raise ServerError(detail=str(e)) from e

    async def get_user_by_email(self, email: str) -> UserEntity | None:
        try:
            stmt = select(UserModel).where(UserModel.email == email)
            result = await self.db.execute(stmt)
            user_model = result.scalar_one_or_none()

            if not user_model:
                return None

            return self._to_domain(user_model)
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
            return self._to_domain(user_model)

        except SQLAlchemyError as e:
            await self.db.rollback()
            raise ServerError(detail=str(e)) from e

    def _to_domain(self, user_model: UserModel) -> UserEntity:
        return UserEntity(
            id=user_model.id,
            name=user_model.name,
            email=user_model.email,
            password=user_model.password,
            avatar=user_model.avatar,
            last_login=user_model.last_login,
            signin_count=user_model.signin_count,
            sign_out_count=user_model.sign_out_count,
            status=user_model.status,
        )
