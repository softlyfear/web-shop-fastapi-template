from sqladmin import ModelView

from app.core import settings
from app.models import Category, Order, OrderItem, Product, Review, User


class BaseAdmin(ModelView):
    can_create = settings.admin.CAN_CREATE
    can_edit = settings.admin.CAN_EDIT
    can_delete = settings.admin.CAN_DELETE
    can_view_details = settings.admin.CAN_VIEW_DETAILS


class UserAdmin(BaseAdmin, model=User):
    column_list = [
        User.id,
        User.username,
        User.email,
        User.is_active,
        User.is_superuser,
    ]

    column_details_exclude_list = [User.hashed_password]
    form_excluded_columns = [User.hashed_password]


class CategoryAdmin(BaseAdmin, model=Category):
    column_list = [
        Category.name,
        Category.slug,
        Category.parent_id,
    ]


class OrderItemAdmin(BaseAdmin, model=OrderItem):
    column_list = "__all__"


class OrderAdmin(BaseAdmin, model=Order):
    column_list = "__all__"


class ProductAdmin(BaseAdmin, model=Product):
    column_list = [
        Product.name,
        Product.slug,
        Product.price,
        Product.category_id,
        Product.stock,
    ]


class ReviewAdmin(BaseAdmin, model=Review):
    column_list = "__all__"
