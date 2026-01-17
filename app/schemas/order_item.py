from app.schemas.base import BaseSchema
from decimal import Decimal


class OrderItemBase(BaseSchema):
    product_id: int
    quantity: int
    price: Decimal


class OrderItemUpdate(BaseSchema):
    product_id: int | None = None
    quantity: int | None = None
    price: Decimal | None = None


class OrderItemRead(OrderItemBase):
    id: int
    order_id: int
