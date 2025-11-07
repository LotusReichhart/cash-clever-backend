import logging

from src.application.interfaces.services import StorageService
from src.core.constants import S3UploadType, S3Path
from src.domain.exceptions.app_exceptions import ServerError, AppError, UnauthorizedError

logger = logging.getLogger(__name__)


class GetListImagesUseCase:
    def __init__(self, storage_service: StorageService):
        self.storage_service = storage_service

    @staticmethod
    def _get_path_from_type(upload_type: S3UploadType) -> str:
        if upload_type == S3UploadType.USER_CATEGORY_ICON:
            return S3Path.USER_CATEGORY_ICONS
        if upload_type == S3UploadType.SYSTEM_CATEGORY_ICON:
            return S3Path.SYSTEM_CATEGORY_ICONS

        logger.error(f"Lỗi logic: Không tìm thấy S3Path cho {upload_type}")
        raise ServerError("Loại upload không được định nghĩa.")

    async def execute(
            self,
            user_id: int,
            upload_type: S3UploadType
    ) -> dict:
        try:
            base_path = self._get_path_from_type(upload_type)
            final_path = base_path

            if upload_type in [
                S3UploadType.USER_CATEGORY_ICON
            ]:
                if not user_id:
                    raise UnauthorizedError()
                final_path = f"{base_path}/{user_id}"

            urls = await self.storage_service.get_files_in_path(path=final_path)

            return {"urls": urls}

        except AppError:
            raise
        except Exception as e:
            logger.error(f"GetListImagesUseCase error: {e}")
            raise ServerError()
