from base import Base, CreateAtMixin, UpdateAtMixin
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import text


class User(Base, CreateAtMixin, UpdateAtMixin):
    email: Mapped[str] = mapped_column(unique=True)
    username: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]
    is_active: Mapped[bool] = mapped_column(server_default=text("true"))
    is_superuser: Mapped[bool] = mapped_column(server_default=text("false"))
