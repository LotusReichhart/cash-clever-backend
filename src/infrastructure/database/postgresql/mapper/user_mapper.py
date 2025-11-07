from src.infrastructure.database.postgresql.models import UserModel
from src.domain.entities import UserEntity

class UserMapper:
    @staticmethod
    def to_user_entity(model: UserModel) -> UserEntity:
        return UserEntity(
            id=model.id,
            name=model.name,
            email=model.email,
            password=model.password,
            avatar=model.avatar,
            last_login=model.last_login,
            signin_count=model.signin_count,
            sign_out_count=model.sign_out_count,
            status=model.status,
        )

    @staticmethod
    def to_user_model(entity: UserEntity) -> UserModel:
        return UserModel(
            id=entity.id,
            name=entity.name,
            email=entity.email,
            password=entity.password,
            avatar=entity.avatar,
            last_login=entity.last_login,
            signin_count=entity.signin_count,
            sign_out_count=entity.sign_out_count,
            status=entity.status,
        )
