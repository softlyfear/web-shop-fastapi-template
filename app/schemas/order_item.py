"""OrderItem Pydantic schemas."""

from datetime import datetime
from decimal import Decimal

from app.schemas import BaseSchema


class OrderItemBase(BaseSchema):
    """Base order item schema."""

    product_id: int
    quantity: int
    price: Decimal | None = None


class OrderItemCreate(OrderItemBase):
    """Schema for order item creation."""

    order_id: int | None = None


class OrderItemUpdate(BaseSchema):
    """Schema for order item update."""

    product_id: int | None = None
    quantity: int | None = None
    price: Decimal | None = None


class OrderItemRead(OrderItemBase):
    """Schema for order item response."""

    id: int
    order_id: int
    created_at: datetime
    updated_at: datetime
