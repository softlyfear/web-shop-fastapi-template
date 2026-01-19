from datetime import datetime
from decimal import Decimal

from app.models import OrderStatus
from app.schemas import BaseSchema


class OrderBase(BaseSchema):
    user_id: int
    status: OrderStatus = OrderStatus.pending
    total_price: Decimal
    shipping_address: str


class OrderCreate(OrderBase):
    pass


class OrderUpdate(BaseSchema):
    user_id: int | None = None
    status: OrderStatus | None = None
    total_price: Decimal | None = None
    shipping_address: str | None = None


class OrderRead(OrderBase):
    id: int
    created_at: datetime
    updated_at: datetime
