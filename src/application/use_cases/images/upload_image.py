import logging
from typing import Optional

from fastapi import UploadFile

from src.application.interfaces.services import StorageService
from src.core.constants import S3UploadType, S3Path
from src.domain.exceptions.app_exceptions import AppError, ServerError

logger = logging.getLogger(__name__)


class UploadImageUseCase:
    def __init__(self, storage_service: StorageService):
        self.storage_service = storage_service

    @staticmethod
    def _get_destination_path(upload_type: S3UploadType) -> str:
        try:
            return getattr(S3Path, upload_type.value)
        except AttributeError:
            logger.error(f"Lỗi logic: Không tìm thấy S3Path cho {upload_type.value}")
            raise ServerError("Lỗi logic: Loại upload không được định nghĩa.")

    async def execute(
            self,
            user_id: int,
            image_file: Optional[UploadFile],
            upload_type: S3UploadType
    ) -> dict:

        try:
            file_url = await self.storage_service.upload_file(
                file=image_file,
                destination_path=f"{self._get_destination_path(upload_type)}/{user_id}"
            )

            return {"url": file_url}

        except AppError:
            raise
        except Exception as e:
            logger.error(f"UploadImageUseCase error: {e}")
            raise ServerError()
