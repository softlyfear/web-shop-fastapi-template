from slugify import slugify
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Category
from app.schemas import CategoryCreate, CategoryUpdate


class CategoryCRUD:
    @staticmethod
    async def create_category(
        session: AsyncSession,
        category_in: CategoryCreate,
    ) -> Category:
        """Создать новую категорию."""
        category_data = category_in.model_dump()
        if not category_data.get("slug"):
            category_data["slug"] = slugify(category_data["name"])
        category = Category(**category_data)
        session.add(category)
        try:
            await session.commit()
        except IntegrityError as exc:
            await session.rollback()
            raise exc
        await session.refresh(category)
        return category

    @staticmethod
    async def get_category(
        session: AsyncSession,
        category_id: int,
    ) -> Category | None:
        """Получить категорию по ID."""
        return await session.get(Category, category_id)

    @staticmethod
    async def get_categories(
        session: AsyncSession,
        offset: int = 0,
        limit: int = 20,
    ) -> list[Category]:
        """Получить список всех категорий."""
        stmt = select(Category).order_by(Category.id).offset(offset).limit(limit)
        result = await session.execute(stmt)
        return list(result.scalars())

    @staticmethod
    async def update_category(
        session: AsyncSession,
        category: Category,
        category_in: CategoryUpdate,
    ) -> Category | None:
        """Обновить категорию по ID."""
        update_data = category_in.model_dump(exclude_unset=True)
        if "name" in update_data and not update_data.get("slug"):
            update_data["slug"] = slugify(update_data["name"])
        for field, value in update_data.items():
            setattr(category, field, value)
        session.add(category)
        try:
            await session.commit()
        except IntegrityError as exc:
            await session.rollback()
            raise exc
        await session.refresh(category)
        return category

    @staticmethod
    async def delete_category(
        session: AsyncSession,
        category: Category,
    ) -> None:
        """Удалить категорию по ID."""
        await session.delete(category)
        await session.commit()


category_crud = CategoryCRUD()
