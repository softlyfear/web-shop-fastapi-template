from typing import Annotated

from sqlalchemy.orm import DeclarativeBase, mapped_column
from datetime import datetime


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)


class CreateAtMixin:
    created_at_type: Annotated[
        datetime,
        mapped_column(
            server_default=text("TIMEZONE('utc', now())"),
            nullable=False,
        ),
    ]


class UpdateAtMixin:
    updated_at: Annotated[
        datetime,
        mapped_column(
            server_default=text("TIMEZONE('utc', now())"),
            onupdate=text("TIMEZONE('utc', now())"),
            nullable=False,
        ),
    ]
