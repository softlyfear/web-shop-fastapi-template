from base import Base, CreateAtMixin, UpdateAtMixin
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from sqlalchemy import text


class User(Base, CreateAtMixin, UpdateAtMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(unique=True)
    username: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]
    is_active: Mapped[bool]
    is_superuser: Mapped[bool]
