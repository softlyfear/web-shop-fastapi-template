"""Order Pydantic schemas."""

from datetime import datetime
from decimal import Decimal

from app.models import OrderStatus
from app.schemas import BaseSchema


class OrderBase(BaseSchema):
    """Base order schema."""

    user_id: int
    status: OrderStatus = OrderStatus.pending
    total_price: Decimal
    shipping_address: str


class OrderCreate(OrderBase):
    """Schema for order creation."""

    pass


class OrderUpdate(BaseSchema):
    """Schema for order update."""

    user_id: int | None = None
    status: OrderStatus | None = None
    total_price: Decimal | None = None
    shipping_address: str | None = None


class OrderRead(OrderBase):
    """Schema for order response."""

    id: int
    created_at: datetime
    updated_at: datetime
