from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import BaseCrud
from app.models import Review
from app.schemas import ReviewCreate, ReviewUpdate


class ReviewCrud(BaseCrud[Review, ReviewCreate, ReviewUpdate]):
    async def get_by_product_id(
        self,
        session: AsyncSession,
        product_id: int,
        offset: int = 0,
        limit: int = 25,
    ) -> list[Review]:
        """Получить все отзывы для продукта."""
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
        """Получить все отзывы пользователя."""
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
        """Проверить, оставлял ли пользователь отзыв на продукт."""
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
        """Создать отзыв с проверкой на дубликаты."""
        existing = await self.get_user_review_for_product(
            session, obj_in.user_id, obj_in.product_id
        )
        if existing:
            raise ValueError(
                "Вы уже оставляли отзыв на этот товар. Используйте редактирование."
            )

        if not 1 <= obj_in.rating <= 5:
            raise ValueError("Рейтинг должен быть от 1 до 5")

        return await self.create(session, obj_in)

    async def get_average_rating(
        self,
        session: AsyncSession,
        product_id: int,
    ) -> float | None:
        """Получить среднюю оценку продукта."""
        stmt = select(func.avg(Review.rating)).where(Review.product_id == product_id)
        result = await session.execute(stmt)
        avg = result.scalar_one()
        return float(avg) if avg else None

    async def get_rating_counts(
        self,
        session: AsyncSession,
        product_id: int,
    ) -> dict[int, int]:
        """Получить количество отзывов для каждой оценки (1-5)."""
        stmt = (
            select(Review.rating, func.count(Review.id))
            .where(Review.product_id == product_id)
            .group_by(Review.rating)
        )
        result = await session.execute(stmt)
        return dict(result.all())


review_crud = ReviewCrud(Review)
