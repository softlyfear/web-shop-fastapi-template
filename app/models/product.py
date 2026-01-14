from base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, text
from datetime import datetime


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    slug: Mapped[str] = mapped_column(unique=True)
    # description: Mapped[Text]
    price: Mapped[int | float]
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    # image: str
    is_active: Mapped[bool]
    stock: Mapped[ist]

    create_at: Mapped[datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', now())"),
    )

    update_at: Mapped[datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', now())"),
    )
