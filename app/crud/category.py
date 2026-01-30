from typing import List

from slugify import slugify
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Category
from app.schemas import CategoryCreate, CategoryUpdate


class CategoryCRUD:
    async def create_category(
        self,
        session: AsyncSession,
        category_in: CategoryCreate,
    ) -> Category:
        """Создать новую категорию."""
        category_data = category_in.model_dump()

        if not category_data.get("slug") or category_data["slug"] == "string":
            category_data["slug"] = slugify(category_data["name"])

        category = Category(**category_data)
        session.add(category)
        await session.commit()
        await session.refresh(category)
        return category

    async def get_category(
        self,
        session: AsyncSession,
        category_id: int,
    ) -> Category | None:
        """Получить категорию по ID."""
        return await session.get(Category, category_id)

    async def get_categories(
        self,
        session: AsyncSession,
        offset: int = 0,
        limit: int = 20,
    ) -> List[Category]:
        """Получить список всех категорий."""
        stmt = select(Category).offset(offset).limit(limit)
        result = await session.execute(stmt)
        return list(result.scalars())

    async def update_category(
        self,
        session: AsyncSession,
        category: Category,
        category_in: CategoryUpdate,
    ) -> Category | None:
        """Обновить продукт по ID."""
        update_data = category_in.model_dump(exclude_unset=True)

        if not update_data.get("slug") or update_data["slug"] == "string":
            update_data["slug"] = slugify(update_data["name"])

        for field, value in update_data.items():
            setattr(category, field, value)

        session.add(category)
        await session.commit()
        await session.refresh(category)
        return category

    async def delete_category(
        self,
        session: AsyncSession,
        category: Category,
    ) -> None:
        """Удалить категорию по ID."""
        await session.delete(category)
        await session.commit()


category_crud = CategoryCRUD()
