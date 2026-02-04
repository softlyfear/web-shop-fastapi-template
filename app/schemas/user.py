from datetime import datetime
from typing import Annotated

from pydantic import EmailStr, Field

from app.schemas import BaseSchema


class UserBase(BaseSchema):
    email: EmailStr
    username: Annotated[str, Field(min_length=3, max_length=20)]


class UserCreate(UserBase):
    password: Annotated[str, Field(min_length=4)]


class UserUpdate(BaseSchema):
    email: EmailStr | None = None
    username: str | None = None


class UserRead(UserBase):
    id: int
    is_active: bool
    is_superuser: bool

    created_at: datetime
    updated_at: datetime


class UserInfo(BaseSchema):
    username: str
    email: str
    logged_in_at: int | None
