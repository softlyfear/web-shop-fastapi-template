"""API v1 router configuration."""

from fastapi import APIRouter

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.carts import router as cart_router
from app.api.v1.endpoints.categories import router as categories_router
from app.api.v1.endpoints.order_items import router as order_item_router
from app.api.v1.endpoints.orders import router as order_router
from app.api.v1.endpoints.products import router as products_router
from app.api.v1.endpoints.reviews import router as review_router
from app.api.v1.endpoints.users import router as users_router

router_v1 = APIRouter()

router_v1.include_router(products_router, prefix="/products", tags=["products"])
router_v1.include_router(categories_router, prefix="/categories", tags=["categories"])
router_v1.include_router(users_router, prefix="/users", tags=["users"])
router_v1.include_router(order_router, prefix="/orders", tags=["orders"])
router_v1.include_router(order_item_router, prefix="/order_items", tags=["order_items"])
router_v1.include_router(review_router, prefix="/reviews", tags=["reviews"])
router_v1.include_router(auth_router, prefix="/auth", tags=["authentication"])
router_v1.include_router(cart_router, prefix="/cart", tags=["cart"])
