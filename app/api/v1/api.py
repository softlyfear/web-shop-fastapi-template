from fastapi import APIRouter

from app.api.v1.endpoints.products import router as products_router

router_v1 = APIRouter()


router_v1.include_router(products_router)
