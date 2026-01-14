from base import Base, CreateAtMixin, UpdateAtMixin
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from sqlalchemy import ForeignKey, text


class Order(Base, CreateAtMixin, UpdateAtMixin):
    __tablename__ = "orders"

    user_id: Mapped[int] = mapped_column(ForeignKey="users.id")
    # status:
    total_price: Mapped[int | float]
    # shipping_addres:
