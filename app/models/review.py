from base import Base, CreateAtMixin
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, Text, CheckConstraint


class Review(Base, CreateAtMixin):
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE")
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    rating: Mapped[int] = mapped_column(CheckConstraint("rating >= 1 AND rating <= 5"))
    comment: Mapped[str] = mapped_column(Text)
