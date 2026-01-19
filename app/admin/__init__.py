from app.admin.auth import AdminAuth
from app.admin.views import (
    CategoryAdmin,
    OrderAdmin,
    OrderItemAdmin,
    ProductAdmin,
    ReviewAdmin,
    UserAdmin,
)

__all__ = [
    "AdminAuth",
]

ALL_ADMIN_VIEWS = [
    UserAdmin,
    CategoryAdmin,
    OrderItemAdmin,
    OrderAdmin,
    ProductAdmin,
    ReviewAdmin,
]
