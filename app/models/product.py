from base import Base, CreateAtMixin, UpdateAtMixin
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, text
from datetime import datetime


class Product(Base, CreateAtMixin, UpdateAtMixin):
    __tablename__ = "products"

    name: Mapped[str]
    slug: Mapped[str] = mapped_column(unique=True)
    # description: Mapped[Text]
    price: Mapped[int | float]
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    # image: str
    is_active: Mapped[bool]
    stock: Mapped[ist]
