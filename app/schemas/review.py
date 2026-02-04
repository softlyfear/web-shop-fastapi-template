from datetime import datetime

from app.schemas import BaseSchema


class ReviewBase(BaseSchema):
    product_id: int
    user_id: int
    rating: int
    comment: str | None


class ReviewCreate(ReviewBase):
    pass


class ReviewUpdate(BaseSchema):
    product_id: int | None = None
    user_id: int | None = None
    rating: int | None = None
    comment: str | None = None


class ReviewRead(ReviewBase):
    id: int
    created_at: datetime
    updated_at: datetime
