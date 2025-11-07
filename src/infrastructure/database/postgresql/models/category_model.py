from sqlalchemy import Index, text, Column, Integer, String, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship, backref

from src.domain.entities import CategoryStatus
from src.infrastructure.database.postgresql import Base


class CategoryModel(Base):
    __tablename__ = "categories"
    __table_args__ = (
        # Index GIN để search/sort tiếng Việt
        Index(
            "idx_category_name_unaccent",
            text("unaccent(name) gin_trgm_ops"),
            postgresql_using="gin"
        ),

        # Index partial: Tên danh mục hệ thống là DUY NHẤT
        Index(
            "uq_system_category_name", "name", unique=True,
            postgresql_where=text("is_system_owned = true")
        ),

        # Index partial: Tên danh mục của user là DUY NHẤT (cho user đó)
        Index(
            "uq_user_category_name_per_user", "user_id", "name",
            unique=True,
            postgresql_where=text("is_system_owned = false")
        )
    )

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    icon_url = Column(String, nullable=True)

    is_system_owned = Column(Boolean, nullable=False, default=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)

    # Quan hệ cha-con
    parent_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=True)

    status = Column(Enum(CategoryStatus), nullable=False, default=CategoryStatus.ACTIVE)

    # Quan hệ đệ quy
    children = relationship(
        "CategoryModel",
        backref=backref("parent", remote_side=[id]),
        cascade="all, delete-orphan"
    )
