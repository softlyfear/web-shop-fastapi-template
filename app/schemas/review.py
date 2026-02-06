"""Review Pydantic schemas."""

from datetime import datetime

from app.schemas import BaseSchema


class ReviewBase(BaseSchema):
    """Base review schema."""

    product_id: int
    user_id: int
    rating: int
    comment: str | None


class ReviewCreate(ReviewBase):
    """Schema for review creation."""

    pass


class ReviewUpdate(BaseSchema):
    """Schema for review update."""

    product_id: int | None = None
    user_id: int | None = None
    rating: int | None = None
    comment: str | None = None


class ReviewRead(ReviewBase):
    """Schema for review response."""

    id: int
    created_at: datetime
    updated_at: datetime
