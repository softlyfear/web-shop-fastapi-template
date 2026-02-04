from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import AuthUtils
from app.crud import BaseCrud
from app.models import User
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


user_crud = UserCrud(User)
