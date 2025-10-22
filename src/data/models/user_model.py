from sqlalchemy import Column, Integer, String, DateTime, Enum
from src.domain.entities import UserStatus
from src.data.db.base import Base


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String, nullable=True)
    avatar = Column(String, nullable=True)
    last_login = Column(DateTime, nullable=True)
    signin_count = Column(Integer, default=0)
    sign_out_count = Column(Integer, default=0)
    status = Column(Enum(UserStatus), nullable=False, default=UserStatus.ACTIVE)
