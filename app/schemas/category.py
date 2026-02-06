"""Category Pydantic schemas."""

from datetime import datetime

from app.schemas import BaseSchema


class CategoryBase(BaseSchema):
    """Base category schema."""

    name: str
    slug: str | None = None


class CategoryCreate(CategoryBase):
    """Schema for category creation."""

    pass


class CategoryUpdate(BaseSchema):
    """Schema for category update."""

    name: str | None = None
    slug: str | None = None


class CategoryRead(CategoryBase):
    """Schema for category response."""

    id: int
    created_at: datetime
    updated_at: datetime
