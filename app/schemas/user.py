"""User Pydantic schemas."""

from datetime import datetime
from typing import Annotated

from pydantic import EmailStr, Field

from app.schemas import BaseSchema


class UserBase(BaseSchema):
    """Base user schema."""

    email: EmailStr
    username: Annotated[str, Field(min_length=3, max_length=20)]


class UserCreate(UserBase):
    """Schema for user registration."""

    password: Annotated[str, Field(min_length=4)]


class UserUpdate(BaseSchema):
    """Schema for user update."""

    email: EmailStr | None = None
    username: str | None = None


class UserRead(UserBase):
    """Schema for user response."""

    id: int
    is_active: bool
    is_superuser: bool

    created_at: datetime
    updated_at: datetime


class UserInfo(BaseSchema):
    """Schema for user session info."""

    username: str
    email: str
    logged_in_at: int | None
