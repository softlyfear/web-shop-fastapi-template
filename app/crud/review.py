"""Review CRUD operations."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import BaseCrud
from app.models import Review
from app.schemas import ReviewCreate, ReviewUpdate


class ReviewCrud(BaseCrud[Review, ReviewCreate, ReviewUpdate]):
    """CRUD operations for Review model."""

    async def get_by_product_id(
        self,
        session: AsyncSession,
        product_id: int,
        offset: int = 0,
        limit: int = 25,
    ) -> list[Review]:
        """Get all reviews for product."""
        stmt = (
            select(Review)
            .where(Review.product_id == product_id)
            .order_by(Review.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_user_id(
        self,
        session: AsyncSession,
        user_id: int,
        offset: int = 0,
        limit: int = 25,
    ) -> list[Review]:
        """Get all user reviews."""
        stmt = (
            select(Review)
            .where(Review.user_id == user_id)
            .order_by(Review.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def get_user_review_for_product(
        self,
        session: AsyncSession,
        user_id: int,
        product_id: int,
    ) -> Review | None:
        """Check if user has reviewed product."""
        stmt = select(Review).where(
            Review.user_id == user_id,
            Review.product_id == product_id,
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_with_validation(
        self,
        session: AsyncSession,
        obj_in: ReviewCreate,
    ) -> Review:
        """Create review with duplicate check."""
        existing = await self.get_user_review_for_product(
            session, obj_in.user_id, obj_in.product_id
        )
        if existing:
            raise ValueError(
                "You have already reviewed this product. Use edit instead."
            )

        if not 1 <= obj_in.rating <= 5:
            raise ValueError("Rating must be between 1 and 5")

        return await self.create(session, obj_in)

    async def get_average_rating(
        self,
        session: AsyncSession,
        product_id: int,
    ) -> float | None:
        """Get product average rating."""
        stmt = select(func.avg(Review.rating)).where(Review.product_id == product_id)
        result = await session.execute(stmt)
        avg = result.scalar_one()
        return float(avg) if avg else None

    async def get_rating_counts(
        self,
        session: AsyncSession,
        product_id: int,
    ) -> dict[int, int]:
        """Get review count for each rating (1-5)."""
        stmt = (
            select(Review.rating, func.count(Review.id))
            .where(Review.product_id == product_id)
            .group_by(Review.rating)
        )
        result = await session.execute(stmt)
        return dict(result.all())


review_crud = ReviewCrud(Review)
