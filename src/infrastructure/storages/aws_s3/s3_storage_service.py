import logging
import os
from typing import List

import aiobotocore
import uuid

from fastapi import UploadFile
from aiobotocore.client import AioBaseClient

from src.application.interfaces.services import StorageService
from src.core.config import settings
from src.domain.exceptions.app_exceptions import ServerError
from src.domain.exceptions.file_exception import FileEmptyError, UnableToUploadFileError, FileTooLargeError

logger = logging.getLogger(__name__)


class S3StorageService(StorageService):
    def __init__(
            self,
            client: AioBaseClient):
        self.client = client
        self.bucket_name = settings.AWS_S3_BUCKET_NAME
        self.region = settings.AWS_S3_REGION
        self.base_url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com"
        self.max_size = 5242880  # 5MB

    @staticmethod
    def _generate_file_name(original_filename: str) -> str:
        extension = original_filename.split(".")[-1]
        return f"{uuid.uuid4()}.{extension}"

    async def upload_file(self, file: UploadFile, destination_path: str) -> str:
        if not file or not file.filename:
            raise FileEmptyError()

        file.file.seek(0, os.SEEK_END)
        file_size = file.file.tell()

        if file_size == 0:
            raise FileEmptyError()

        if file_size > self.max_size:
            raise FileTooLargeError()

        file.file.seek(0, os.SEEK_SET)

        file_name = self._generate_file_name(file.filename)
        file_key = f"{destination_path}/{file_name}"
        file_content = await file.read()

        try:
            await self.client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=file_content,
                ContentType=file.content_type,
                ACL='public-read'
            )
        except Exception as e:
            logger.error(f"S3StorageService upload_file error: {e}")
            raise UnableToUploadFileError

        return f"{self.base_url}/{file_key}"

    async def delete_file(self, file_url: str) -> bool:
        base_url_prefix = f"{self.base_url}/"
        if not file_url or not file_url.startswith(base_url_prefix):
            logger.warning(f"URL không hợp lệ hoặc không thuộc bucket này: {file_url}")
            return False

        file_key = file_url.replace(base_url_prefix, "")

        if not file_key:
            logger.error(f"Không thể trích xuất file_key từ URL: {file_url}")
            return False

        try:
            await self.client.delete_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            logger.info(f"Đã xóa file thành công khỏi S3: {file_key}")
            return True
        except Exception as e:
            logger.error(f"S3StorageService delete_file error: {e}")
            raise ServerError

    async def get_files_in_path(self, path: str) -> List[str]:
        if not path:
            return []

        if not path.endswith('/'):
            path += '/'

        urls = []
        try:
            response = await self.client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=path
            )

            for file_obj in response.get('Contents', []):
                file_key = file_obj.get('Key')
                if file_key and not file_key.endswith('/'):
                    urls.append(f"{self.base_url}/{file_key}")

            return urls

        except Exception as e:
            logger.error(f"S3StorageService get_files_in_path error: {e}")
            raise ServerError("Lỗi khi lấy danh sách ảnh")
