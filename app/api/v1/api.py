from fastapi import APIRouter

from app.api.v1.endpoints.categories import router as categories_router
from app.api.v1.endpoints.products import router as products_router
from app.api.v1.endpoints.users import router as users_router

router_v1 = APIRouter()


router_v1.include_router(products_router)
router_v1.include_router(categories_router)
router_v1.include_router(users_router)
