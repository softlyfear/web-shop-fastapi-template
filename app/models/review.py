from base import Base, CreateAtMixin
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, text
from datetime import datetime


class Review(Base, CreateAtMixin):
    __tablename__ = "reviews"

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    # rating: Mapped[int] = mapped_column(
    # comment:
