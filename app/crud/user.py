from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models import User
from app.schemas import UserCreate, UserUpdate


class UserCRUD:
    async def create_user(
        self,
        session: AsyncSession,
        user_in: UserCreate,
    ) -> User:
        """Создать пользователя."""
        user_data = user_in.model_dump(exclude={"password"})
        hashed = hash_password(user_in.password)
        user = User(**user_data, hashed_password=hashed)
        user = User(**user_data, hashed_password=hashed)
        session.add(user)
        try:
            await session.commit()
        except IntegrityError as exc:
            await session.rollback()
            raise exc
        except ValueError as exc:
            await session.rollback()
            raise exc
        await session.refresh(user)
        return user

    async def get_user(
        self,
        session: AsyncSession,
        user_id: int,
    ) -> User | None:
        """Получить пользователя по ID."""
        return await session.get(User, user_id)

    async def get_users(
        self,
        session: AsyncSession,
        offset: int = 20,
        limit: int = 0,
    ) -> list[User]:
        """Получить список пользователей."""
        stmt = select(User).order_by(User.id).offset(offset).limit(limit)
        result = await session.execute(stmt)
        return list(result.scalars())

    async def update_user(
        self,
        session: AsyncSession,
        user: User,
        user_in: UserUpdate,
    ) -> User | None:
        """Обновить пользователя по ID"""
        user_data = user_in.model_dump(exclude_unset=True)
        for field, value in user_data.items():
            setattr(user, field, value)
        session.add(user)
        try:
            await session.commit()
        except IntegrityError as exc:
            await session.rollback()
            raise exc
        await session.refresh(user)
        return user

    async def delete_user(
        self,
        session: AsyncSession,
        user: User,
    ) -> None:
        """Удалить пользователя по ID."""
        await session.delete(user)
        await session.commit()


user_crud = UserCRUD()
