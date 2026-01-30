from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.product import Product

from app.models import Base, CreateAtMixin, UpdateAtMixin, str_255


class Category(Base, CreateAtMixin, UpdateAtMixin):
    __tablename__ = "categories"  # type: ignore

    name: Mapped[str_255] = mapped_column(unique=True)
    slug: Mapped[str_255 | None] = mapped_column(unique=True)

    products: Mapped[list["Product"]] = relationship(
        "Product",
        back_populates="category",
        cascade="all, delete-orphan",
    )

    def __str__(self) -> str:
        return self.name
