from typing import Annotated

from sqlalchemy import String, Numeric, Integer, text
from sqlalchemy.orm import (
    DeclarativeBase,
    mapped_column,
    declared_attr,
    Mapped,
)
from datetime import datetime


str_255 = Annotated[str, 255]
num_10_2 = Annotated[float, 10]


class Base(DeclarativeBase):
    __abstract__ = True

    type_annotation_map = {
        str_255: String(255),
        num_10_2: Numeric(precision=10, scale=2),
    }

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{cls.__name__.lower()}s"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)


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
