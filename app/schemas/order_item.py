from datetime import datetime
from decimal import Decimal

from app.schemas import BaseSchema


class OrderItemBase(BaseSchema):
    product_id: int
    quantity: int
    price: Decimal | None = None


class OrderItemCreate(OrderItemBase):
    order_id: int | None = None


class OrderItemUpdate(BaseSchema):
    product_id: int | None = None
    quantity: int | None = None
    price: Decimal | None = None


class OrderItemRead(OrderItemBase):
    id: int
    order_id: int
    created_at: datetime
    updated_at: datetime
