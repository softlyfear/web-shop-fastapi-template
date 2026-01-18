import enum

from sqlalchemy import Enum, ForeignKey, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base, CreateAtMixin, UpdateAtMixin, num_10_2


class OrderStatus(enum.Enum):
    pending = "pending"
    paid = "paid"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"


class Order(Base, CreateAtMixin, UpdateAtMixin):
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus), default=OrderStatus.pending, server_default=text("'pending'")
    )

    total_price: Mapped[num_10_2]
    shipping_address: Mapped[str] = mapped_column(Text)
