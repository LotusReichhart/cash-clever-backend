from fastapi import FastAPI, Request
from slowapi.errors import RateLimitExceeded

from src.core.config import settings
from src.app.container import Container
from src.core.exceptions import AppError
from src.core.lifespan import lifespan
from src.core.limiter import limiter
from src.core.logging import setup_logging
from src.presentation.api.middlewares.auth_middleware import AuthMiddleware

from src.schemas.error_response import ErrorResponse

from src.presentation.api import api_router


def create_app() -> FastAPI:
    container = Container()
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        lifespan=lifespan
    )

    app.state.limiter = limiter

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
        return ErrorResponse(
            status=429,
            message="Too Many Requests",
            errors={"message": "Bạn đang thao tác quá nhanh. Vui lòng thử lại sau ít phút."}
        )

    @app.middleware("http")
    async def app_error_handler(request: Request, call_next):
        try:
            return await call_next(request)
        except AppError as e:
            return ErrorResponse(
                status=e.status_code,
                message=e.message,
                errors=e.errors
            )
        except Exception as e:
            return ErrorResponse(
                status=500,
                message="Internal Server Error",
                errors={"system": str(e)}
            )

    app.container = container
    app.add_middleware(AuthMiddleware)

    app.include_router(api_router)

    setup_logging()
    return app


app = create_app()
