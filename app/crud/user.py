from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import AuthUtils
from app.crud import BaseCrud
from app.models import Order, Review, User
from app.schemas import UserCreate, UserUpdate


class UserCrud(BaseCrud[User, UserCreate, UserUpdate]):
    def _prepare_create_data(self, obj_in: UserCreate) -> dict:
        data = obj_in.model_dump(exclude={"password"})
        data["hashed_password"] = AuthUtils.hash_password(obj_in.password)
        return data

    async def get_user_by_username(
        self,
        session: AsyncSession,
        username: str,
    ) -> User | None:
        """Находит пользователя по username."""
        stmt = select(User).where(User.username == username)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_by_email(
        self,
        session: AsyncSession,
        email: str,
    ) -> User | None:
        """Находит пользователя по email."""
        stmt = select(User).where(User.email == email)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_password(
        self,
        session: AsyncSession,
        user: User,
        new_password: str,
    ) -> User:
        """Обновить пароль пользователя."""
        user.hashed_password = AuthUtils.hash_password(new_password)
        return await self._commit_refresh(session, user)

    async def toggle_active_status(
        self,
        session: AsyncSession,
        user: User,
    ) -> User:
        """Переключить статус активности пользователя."""
        user.is_active = not user.is_active
        return await self._commit_refresh(session, user)

    async def get_active_users(
        self,
        session: AsyncSession,
        offset: int = 0,
        limit: int = 25,
    ) -> list[User]:
        """Получить только активных пользователей."""
        stmt = (
            select(User)
            .where(User.is_active)
            .order_by(User.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def get_user_statistics(
        self,
        session: AsyncSession,
        user_id: int,
    ) -> dict:
        """Получить статистику пользователя (количество заказов,
        отзывов и потраченных денег)."""
        from app.models import OrderStatus

        # Общее количество заказов
        orders_stmt = select(func.count(Order.id)).where(Order.user_id == user_id)
        orders_result = await session.execute(orders_stmt)
        total_orders = orders_result.scalar_one()

        # Количество заказов в ожидании (pending)
        pending_stmt = select(func.count(Order.id)).where(
            Order.user_id == user_id, Order.status == OrderStatus.pending
        )
        pending_result = await session.execute(pending_stmt)
        pending_orders = pending_result.scalar_one()

        # Количество завершенных заказов (delivered)
        completed_stmt = select(func.count(Order.id)).where(
            Order.user_id == user_id, Order.status == OrderStatus.delivered
        )
        completed_result = await session.execute(completed_stmt)
        completed_orders = completed_result.scalar_one()

        # Общая сумма потраченных денег (только оплаченные: paid)
        total_spent_stmt = select(func.sum(Order.total_price)).where(
            Order.user_id == user_id, Order.status == OrderStatus.paid
        )
        total_spent_result = await session.execute(total_spent_stmt)
        total_spent = total_spent_result.scalar_one() or 0

        # Количество отзывов
        reviews_stmt = select(func.count(Review.id)).where(Review.user_id == user_id)
        reviews_result = await session.execute(reviews_stmt)
        reviews_count = reviews_result.scalar_one()

        return {
            "user_id": user_id,
            "total_orders": total_orders,
            "pending_orders": pending_orders,
            "completed_orders": completed_orders,
            "total_spent": float(total_spent),
            "total_reviews": reviews_count,
        }


user_crud = UserCrud(User)
