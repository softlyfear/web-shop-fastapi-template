from fastapi import APIRouter

from app.web.catalog import router as catalog_router
from app.web.product import router as product_router

router = APIRouter()

router.include_router(catalog_router, tags=["catalog"])
router.include_router(product_router, tags=["product"])
