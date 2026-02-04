import uuid
from pathlib import Path

import aiofiles
from markupsafe import Markup
from slugify import slugify
from sqladmin import ModelView
from wtforms import FileField

from app.core import settings
from app.models import Category, Order, OrderItem, Product, Review, User

UPLOAD_DIR = Path("app/static/img/products")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


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
    name_plural = "Categories"

    column_list = [
        Category.name,
        Category.slug,
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
        Product.id,
        Product.name,
        Product.image,
        Product.category,
        Product.price,
        Product.stock,
        Product.is_active,
    ]

    form_overrides = {"image": FileField}

    form_args = {
        "image": {
            "label": "Изображение",
            "render_kw": {"accept": "image/*"},
        }
    }

    column_formatters = {
        "image": lambda m, a: (
            Markup(f'<img src="/static/img/products/{m.image}" height="40">')
            if m.image
            else "—"
        )
    }

    async def insert_model(self, request, data):
        if not data.get("slug"):
            data["slug"] = slugify(data.get("name", ""))

        image_file = data.get("image")
        if image_file and hasattr(image_file, "filename") and image_file.filename:
            ext = image_file.filename.rsplit(".", 1)[-1].lower()
            filename = f"{uuid.uuid4()}.{ext}"
            filepath = UPLOAD_DIR / filename

            if hasattr(image_file, "read"):
                content = await image_file.read()
            else:
                content = image_file.file.read()

            async with aiofiles.open(filepath, "wb") as f:
                await f.write(content)

            data["image"] = filename
        else:
            data.pop("image", None)

        return await super().insert_model(request, data)

    async def update_model(self, request, pk, data):
        if not data.get("slug"):
            data["slug"] = slugify(data.get("name", ""))

        image_file = data.get("image")
        if image_file and hasattr(image_file, "filename") and image_file.filename:
            ext = image_file.filename.rsplit(".", 1)[-1].lower()
            filename = f"{uuid.uuid4()}.{ext}"
            filepath = UPLOAD_DIR / filename

            if hasattr(image_file, "read"):
                content = await image_file.read()
            else:
                content = image_file.file.read()

            async with aiofiles.open(filepath, "wb") as f:
                await f.write(content)

            data["image"] = filename
        else:
            data.pop("image", None)

        return await super().update_model(request, pk, data)


class ReviewAdmin(BaseAdmin, model=Review):
    column_list = [
        Review.product,
        Review.User,
        Review.rating,
        Review.comment,
    ]
