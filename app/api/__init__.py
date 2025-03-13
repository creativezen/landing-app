from core.config import settings
from fastapi import APIRouter

from .auth import router as router_auth

router = APIRouter(
    prefix=settings.api.prefix,
)

router.include_router(router=router_auth)
# router.include_router(router=router_landing)
