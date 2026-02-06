"""Category CRUD operations."""

from slugify import slugify
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud import BaseCrud
from app.models import Category, Product
from app.schemas import CategoryCreate, CategoryUpdate


class CategoryCrud(BaseCrud[Category, CategoryCreate, CategoryUpdate]):
    """CRUD operations for Category model."""

    def _prepare_create_data(self, obj_in: CategoryCreate) -> dict:
        data = obj_in.model_dump()
        if not data.get("slug"):
            data["slug"] = slugify(data["name"])
        return data

    def _prepare_update_data(self, obj_in: CategoryUpdate) -> dict:
        data = obj_in.model_dump(exclude_unset=True)
        if "name" in data and not data.get("slug"):
            data["slug"] = slugify(data["name"])
        return data

    async def get_by_slug(
        self,
        session: AsyncSession,
        slug: str,
    ) -> Category | None:
        """Get category by slug."""
        stmt = select(Category).where(Category.slug == slug)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_with_products(
        self,
        session: AsyncSession,
        category_id: int,
    ) -> Category | None:
        """Get category with all products (eager loading)."""
        stmt = (
            select(Category)
            .where(Category.id == category_id)
            .options(selectinload(Category.products))
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_categories_with_product_count(
        self,
        session: AsyncSession,
    ) -> list[dict]:
        """Get categories with active product count."""
        stmt = (
            select(
                Category.id,
                Category.name,
                Category.slug,
                func.count(Product.id).label("product_count"),
            )
            .outerjoin(
                Product,
                (Product.category_id == Category.id) & (Product.is_active),
            )
            .group_by(Category.id, Category.name, Category.slug)
            .order_by(Category.name)
        )
        result = await session.execute(stmt)

        return [
            {
                "id": row.id,
                "name": row.name,
                "slug": row.slug,
                "product_count": row.product_count,
            }
            for row in result.all()
        ]


category_crud = CategoryCrud(Category)
