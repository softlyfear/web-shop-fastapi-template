from datetime import datetime
from typing import Annotated

from sqlalchemy import Integer, Numeric, String, text
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
)

str_255 = Annotated[str, 255]
num_10_2 = Annotated[float, 10]


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    type_annotation_map = {
        str_255: String(255),
        num_10_2: Numeric(precision=10, scale=2, asdecimal=True),
    }

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{cls.__name__.lower()}s"


class CreateAtMixin:
    created_at: Mapped[datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', now())"),
        nullable=False,
    )


class UpdateAtMixin:
    updated_at: Mapped[datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', now())"),
        onupdate=text("TIMEZONE('utc', now())"),
        nullable=False,
    )
