from enum import Enum


class S3Path:
    _avatars = "avatars"
    _icons = "icons"

    USER_AVATAR = f"{_avatars}/users"

    USER_CATEGORY_ICONS = f"{_icons}/categories/users"

    SYSTEM_CATEGORY_ICONS = f"{_icons}/categories/systems"

class S3UploadType(str, Enum):
    USER_CATEGORY_ICON = "user-category-icon"
    SYSTEM_CATEGORY_ICON = "system-category-icon"

