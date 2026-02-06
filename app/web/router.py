"""Web router configuration."""

from fastapi import APIRouter

from app.web.account import router as account_router
from app.web.auth import router as auth_router
from app.web.cart import router as cart_router
from app.web.catalog import router as catalog_router
from app.web.checkout import router as checkout_router
from app.web.home import router as home_router
from app.web.product import router as product_router

router = APIRouter()

router.include_router(catalog_router, prefix="/catalog", tags=["web"])
router.include_router(home_router, tags=["web"])
router.include_router(auth_router, prefix="/auth", tags=["web"])
router.include_router(cart_router, prefix="/cart", tags=["web"])
router.include_router(checkout_router, prefix="/checkout", tags=["web"])
router.include_router(product_router, prefix="/product", tags=["web"])
router.include_router(account_router, prefix="/account", tags=["web"])
