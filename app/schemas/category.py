from datetime import datetime

from app.schemas import BaseSchema


class CategoryBase(BaseSchema):
    name: str
    slug: str
    parent_id: int | None = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseSchema):
    name: str | None = None
    slug: str | None = None
    parent_id: int | None = None


class CategoryRead(CategoryBase):
    id: int
    parent_id: int | None = None
    created_at: datetime
    updated_at: datetime
