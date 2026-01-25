from datetime import datetime

from pydantic import EmailStr

from app.schemas import BaseSchema


class UserBase(BaseSchema):
    email: EmailStr
    username: str
    is_active: bool
    is_superuser: bool


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseSchema):
    email: EmailStr | None = None
    username: str | None = None
    is_active: bool | None = None
    is_superuser: bool | None = None


class UserRead(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
