from fastapi import APIRouter

from .signup import router as signup_router
from .signin import router as signin_router
from .password import router as password_router
from .otp import router as otp_router
from .refresh import router as refresh_router
from .sign_out import router as sign_out_router
from .google import router as google_router

auth_router = APIRouter(prefix="/auth", tags=["Auth"])

auth_router.include_router(signup_router)
auth_router.include_router(signin_router)
auth_router.include_router(password_router)
auth_router.include_router(otp_router)
auth_router.include_router(refresh_router)
auth_router.include_router(sign_out_router)
auth_router.include_router(google_router)
