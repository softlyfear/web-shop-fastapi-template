from base import Base, CreateAtMixin, UpdateAtMixin
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


class Category(Base, CreateAtMixin, UpdateAtMixin):
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(nullable=False)
    slug: Mapped[str] = mapped_column(unique=True, nullable=False)

    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id"),
        nullable=True,
    )
