from fastapi import APIRouter

from app.web.auth import router as auth_router
from app.web.catalog import router as catalog_router
from app.web.home import router as home_router

router = APIRouter()

router.include_router(catalog_router, tags=["catalog"])
router.include_router(home_router, tags=["home"])
router.include_router(auth_router, tags=["auth"])
