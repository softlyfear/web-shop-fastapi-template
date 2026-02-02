from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.category import Category

from app.models import Base, CreateAtMixin, UpdateAtMixin, num_10_2, str_255


class Product(Base, CreateAtMixin, UpdateAtMixin):
    name: Mapped[str_255]
    slug: Mapped[str_255 | None] = mapped_column(unique=True)
    description: Mapped[str | None] = mapped_column(Text)
    price: Mapped[num_10_2]
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE")
    )
    image: Mapped[str_255 | None]
    is_active: Mapped[bool] = mapped_column(server_default=text("true"))
    stock: Mapped[int] = mapped_column(default=0)

    category: Mapped[Category] = relationship("Category", back_populates="products")

    def __str__(self) -> str:
        return self.name
