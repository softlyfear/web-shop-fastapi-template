from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base, CreateAtMixin

if TYPE_CHECKING:
    from app.models import Product, User


class Review(Base, CreateAtMixin):
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE")
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    rating: Mapped[int] = mapped_column(CheckConstraint("rating >= 1 AND rating <= 5"))
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    product: Mapped[Product] = relationship("Product")
    User: Mapped[User] = relationship("User")
