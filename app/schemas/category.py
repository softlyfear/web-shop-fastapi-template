from datetime import datetime

from app.schemas import BaseSchema


class CategoryBase(BaseSchema):
    name: str
    slug: str | None = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseSchema):
    name: str | None = None
    slug: str | None = None


class CategoryRead(CategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime
