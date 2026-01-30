from slugify import slugify
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
        User.username,
        User.email,
        User.is_active,
        User.is_superuser,
        User.id,
    ]

    column_details_exclude_list = [User.hashed_password]
    form_excluded_columns = [User.hashed_password]


class CategoryAdmin(BaseAdmin, model=Category):
    column_list = [
        Category.name,
        Category.products,
        Category.id,
    ]

    async def insert_model(self, request, data):
        """Авто-генерация slug"""
        if not data.get("slug"):
            data["slug"] = slugify(data.get("name", ""))
        return await super().insert_model(request, data)

    form_excluded_columns = [Category.products]


class OrderItemAdmin(BaseAdmin, model=OrderItem):
    column_list = [
        OrderItem.product,
        OrderItem.quantity,
        OrderItem.price,
        OrderItem.order_id,
        OrderItem.product_id,
    ]


class OrderAdmin(BaseAdmin, model=Order):
    column_list = [
        Order.user,
        Order.items,
        Order.total_price,
        Order.status,
        Order.shipping_address,
        Order.id,
    ]

    form_widget_args = {"items": {"disabled": False}}


class ProductAdmin(BaseAdmin, model=Product):
    column_list = [
        Product.name,
        Product.category,
        Product.price,
        Product.description,
        Product.stock,
        Product.is_active,
        Product.category_id,
        Product.id,
    ]

    async def insert_model(self, request, data):
        """Авто-генерация slug"""
        if not data.get("slug"):
            data["slug"] = slugify(data.get("name", ""))
        return await super().insert_model(request, data)


class ReviewAdmin(BaseAdmin, model=Review):
    column_list = [
        Review.product,
        Review.User,
        Review.rating,
        Review.comment,
    ]
