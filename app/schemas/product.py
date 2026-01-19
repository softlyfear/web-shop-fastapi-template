from datetime import datetime
from decimal import Decimal

from app.schemas import BaseSchema


class ProductBase(BaseSchema):
    name: str
    slug: str
    description: str | None = None
    price: Decimal
    category_id: int
    image: str | None = None
    is_active: bool
    stock: int


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseSchema):
    name: str | None = None
    slug: str | None = None
    description: str | None = None
    price: Decimal | None = None
    category_id: int | None = None
    image: str | None = None
    is_active: bool | None = None
    stock: int | None = None


class ProductRead(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime
