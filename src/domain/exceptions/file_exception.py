from src.domain.exceptions.app_exceptions import BadRequestError


class FileEmptyError(BadRequestError):
    error = "Vui lòng nhập file của bạn"

    def __init__(self):
        super().__init__(errors={"file": self.error})


class FileTooLargeError(BadRequestError):
    error = "File có dung lượng quá lớn"

    def __init__(self):
        super().__init__(errors={"file": self.error})


class UnableToUploadFileError(BadRequestError):
    error = "Không thể xử lý file của bạn"

    def __init__(self):
        super().__init__(errors={"file": self.error})
