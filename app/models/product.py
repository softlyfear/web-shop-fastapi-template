from app.models.base import Base, CreateAtMixin, UpdateAtMixin, str_255, num_10_2
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, Text, text


class Product(Base, CreateAtMixin, UpdateAtMixin):
    name: Mapped[str_255]
    slug: Mapped[str_255] = mapped_column(unique=True)
    description: Mapped[str | None] = mapped_column(Text)
    price: Mapped[num_10_2]
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE")
    )
    image: Mapped[str_255 | None]
    is_active: Mapped[bool] = mapped_column(server_default=text("true"))
    stock: Mapped[int] = mapped_column(default=0)
