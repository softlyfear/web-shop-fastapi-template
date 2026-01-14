from base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, text
from datetime import datetime


class OrderItem(Base):
    __tablename__ = "order_items"

    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int0]
    # price: Mapped[int | float]
