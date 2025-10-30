from fastapi import APIRouter

from api.routes import login, private, users, utils
from core.config import settings

api_router = APIRouter()

api_router.include_router(login.router)

api_router.include_router(users.router)
api_router.include_router(users.admin_router)

api_router.include_router(utils.router)

if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
