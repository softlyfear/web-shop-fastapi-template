"""Order model and status enum."""

import enum
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models import OrderItem, User


from app.models import Base, CreateAtMixin, UpdateAtMixin, num_10_2


class OrderStatus(enum.Enum):
    """Order status enumeration."""

    pending = "pending"
    paid = "paid"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"


class Order(Base, CreateAtMixin, UpdateAtMixin):
    """Customer order model."""

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus),
        default=OrderStatus.pending,
        server_default=text("'pending'"),
    )
    total_price: Mapped[num_10_2]
    shipping_address: Mapped[str] = mapped_column(Text)

    items: Mapped[list[OrderItem]] = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )

    user: Mapped[User] = relationship("User")

    def __str__(self) -> str:
        return f"Order #{self.id} - {self.status.value} - ${self.total_price}"
