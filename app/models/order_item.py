from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.order import Order
    from app.models.product import Product

from app.models.base import Base, num_10_2


class OrderItem(Base):
    __tablename__ = "order_items"  # type: ignore

    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"))
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE")
    )
    quantity: Mapped[int]
    price: Mapped[num_10_2]

    order: Mapped["Order"] = relationship("Order", back_populates="items")
    product: Mapped["Product"] = relationship("Product")

    def __str__(self) -> str:
        return f"{self.quantity}x Product #{self.product_id} (${self.price})"
