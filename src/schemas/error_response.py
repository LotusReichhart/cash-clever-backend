from fastapi.responses import JSONResponse

class ErrorResponse(JSONResponse):
    def __init__(self, status: int, message: str, errors: dict | None = None):
        content = {
            "status": status,
            "message": message,
            "errors": errors or {}
        }
        super().__init__(status_code=status, content=content)
