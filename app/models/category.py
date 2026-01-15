from base import Base, CreateAtMixin, UpdateAtMixin, str_255
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


class Category(Base, CreateAtMixin, UpdateAtMixin):
    __tablename__ = "categories"

    name: Mapped[str_255]
    slug: Mapped[str_255] = mapped_column(unique=True)

    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE")
    )
