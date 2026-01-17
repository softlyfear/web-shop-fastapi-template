from app.models.base import Base, num_10_2
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey


class OrderItem(Base):
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"))
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE")
    )
    quantity: Mapped[int]
    price: Mapped[num_10_2]
