"""Product Pydantic schemas."""

from datetime import datetime
from decimal import Decimal

from app.schemas import BaseSchema


class ProductBase(BaseSchema):
    """Base product schema."""

    name: str
    slug: str | None = None
    description: str | None = None
    price: Decimal
    category_id: int
    image: str | None = None
    is_active: bool
    stock: int


class ProductCreate(ProductBase):
    """Schema for product creation."""

    pass


class ProductUpdate(BaseSchema):
    """Schema for product update."""

    name: str | None = None
    slug: str | None = None
    description: str | None = None
    price: Decimal | None = None
    category_id: int | None = None
    image: str | None = None
    is_active: bool | None = None
    stock: int | None = None


class ProductRead(ProductBase):
    """Schema for product response."""

    id: int
    created_at: datetime
    updated_at: datetime
