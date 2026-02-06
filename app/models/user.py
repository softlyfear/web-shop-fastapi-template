"""User model."""

from sqlalchemy import text
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base, CreateAtMixin, UpdateAtMixin


class User(Base, CreateAtMixin, UpdateAtMixin):
    """User account model."""

    email: Mapped[str] = mapped_column(unique=True)
    username: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]
    is_active: Mapped[bool] = mapped_column(server_default=text("true"))
    is_superuser: Mapped[bool] = mapped_column(server_default=text("false"))

    def __str__(self) -> str:
        return self.username
