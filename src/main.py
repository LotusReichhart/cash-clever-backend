from fastapi import FastAPI
from src.core.config import settings
from src.interfaces.api.v1.hello_routes import router as hello_router

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
    )
    app.include_router(hello_router, prefix="/api/v1", tags=["Hello"])
    return app

app = create_app()
