from app.crud import BaseCrud
from app.models import Review
from app.schemas import ReviewCreate, ReviewUpdate


class ReviewCrud(BaseCrud[Review, ReviewCreate, ReviewUpdate]):
    pass


review = ReviewCrud(Review)
