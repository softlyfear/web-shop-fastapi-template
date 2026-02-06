"""Product CRUD operations."""

from slugify import slugify
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud import BaseCrud
from app.models import Product
from app.schemas import ProductCreate, ProductUpdate


class ProductCrud(BaseCrud[Product, ProductCreate, ProductUpdate]):
    """CRUD operations for Product model."""

    def _prepare_create_data(self, obj_in: ProductCreate) -> dict:
        data = obj_in.model_dump()
        if not data.get("slug"):
            data["slug"] = slugify(data["name"])
        return data

    def _prepare_update_data(self, obj_in: ProductUpdate) -> dict:
        data = obj_in.model_dump(exclude_unset=True)
        if "name" in data and not data.get("slug"):
            data["slug"] = slugify(data["name"])
        return data

    async def get_by_slug(
        self,
        session: AsyncSession,
        slug: str,
    ) -> Product | None:
        """Get product by slug."""
        stmt = (
            select(Product)
            .where(Product.slug == slug)
            .options(selectinload(Product.category))
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_category(
        self,
        session: AsyncSession,
        category_id: int,
        offset: int = 0,
        limit: int = 25,
        only_active: bool = True,
    ) -> list[Product]:
        """Get products by category."""
        stmt = select(Product).where(Product.category_id == category_id)

        if only_active:
            stmt = stmt.where(Product.is_active)

        stmt = stmt.order_by(Product.created_at.desc()).offset(offset).limit(limit)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def search_products(
        self,
        session: AsyncSession,
        search_query: str | None = None,
        category_id: int | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        only_active: bool = True,
        sort_by: str = "created_at_desc",
        offset: int = 0,
        limit: int = 25,
    ) -> list[Product]:
        """Search and filter products.

        Args:
            search_query: Search query for name or description.
            category_id: Filter by category.
            min_price: Minimum price.
            max_price: Maximum price.
            only_active: Only active products.
            sort_by: Sort order.
            offset: Pagination offset.
            limit: Results limit.
        """
        stmt = select(Product)

        # Filters
        filters = []

        if only_active:
            filters.append(Product.is_active)

        if search_query:
            search_pattern = f"%{search_query}%"
            filters.append(
                or_(
                    Product.name.ilike(search_pattern),
                    Product.description.ilike(search_pattern),
                )
            )

        if category_id is not None:
            filters.append(Product.category_id == category_id)

        if min_price is not None:
            filters.append(Product.price >= min_price)

        if max_price is not None:
            filters.append(Product.price <= max_price)

        if filters:
            stmt = stmt.where(and_(*filters))

        # Sorting
        sort_mapping = {
            "price_asc": Product.price.asc(),
            "price_desc": Product.price.desc(),
            "newest": Product.created_at.desc(),
            "oldest": Product.created_at.asc(),
            "name_asc": Product.name.asc(),
            "name_desc": Product.name.desc(),
        }

        order_by = sort_mapping.get(sort_by, Product.created_at.desc())
        stmt = stmt.order_by(order_by)

        # Pagination
        stmt = stmt.offset(offset).limit(limit)

        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def get_active_products(
        self,
        session: AsyncSession,
        offset: int = 0,
        limit: int = 25,
    ) -> list[Product]:
        """Get only active products."""
        stmt = (
            select(Product)
            .where(Product.is_active)
            .order_by(Product.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def get_low_stock_products(
        self,
        session: AsyncSession,
        threshold: int = 10,
        offset: int = 0,
        limit: int = 25,
    ) -> list[Product]:
        """Get products with low stock."""
        stmt = (
            select(Product)
            .where(Product.stock <= threshold, Product.is_active)
            .order_by(Product.stock.asc())
            .offset(offset)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def update_stock(
        self,
        session: AsyncSession,
        product_id: int,
        quantity_change: int,
    ) -> Product:
        """Update product stock.

        Args:
            product_id: Product ID.
            quantity_change: Quantity change (positive to add, negative to reduce).
        """
        product = await self.get(session, product_id)
        if not product:
            raise ValueError(f"Product with id {product_id} not found")

        new_stock = product.stock + quantity_change
        if new_stock < 0:
            raise ValueError(
                f"Cannot reduce stock below 0. "
                f"Current: {product.stock}, change: {quantity_change}"
            )

        product.stock = new_stock
        return await self._commit_refresh(session, product)


product_crud = ProductCrud(Product)
