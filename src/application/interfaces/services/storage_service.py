from abc import ABC, abstractmethod
from typing import List

from fastapi import UploadFile


class StorageService(ABC):
    @abstractmethod
    async def upload_file(
            self,
            file: UploadFile,
            destination_path: str
    ) -> str:
        raise NotImplementedError

    @abstractmethod
    async def delete_file(self, file_url: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def get_files_in_path(self, path: str) -> List[str]:
        raise NotImplementedError
