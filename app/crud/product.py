from slugify import slugify
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Product
from app.schemas import ProductCreate, ProductUpdate


class ProductCRUD:
    async def create_product(
        self,
        session: AsyncSession,
        product_in: ProductCreate,
    ) -> Product:
        """Создать новый продукт."""
        product_data = product_in.model_dump()
        if not product_data.get("slug"):
            product_data["slug"] = slugify(product_data["name"])
        product = Product(**product_data)
        session.add(product)
        try:
            await session.commit()
        except IntegrityError as exc:
            await session.rollback()
            raise exc
        await session.refresh(product)
        return product

    async def get_product(
        self,
        session: AsyncSession,
        product_id: int,
    ) -> Product | None:
        """Получить продукт по ID."""
        return await session.get(Product, product_id)

    async def get_products(
        self,
        session: AsyncSession,
        offset: int = 0,
        limit: int = 20,
    ) -> list[Product]:
        """Получить все продукты."""
        stmt = select(Product).order_by(Product.id).offset(offset).limit(limit)
        result = await session.execute(stmt)
        return list(result.scalars())

    async def update_product(
        self,
        session: AsyncSession,
        product: Product,
        product_in: ProductUpdate,
    ) -> Product | None:
        """Обновить продукт по ID."""
        update_data = product_in.model_dump(exclude_unset=True)
        if "name" in update_data and not update_data.get("slug"):
            update_data["slug"] = slugify(update_data["name"])
        for field, value in update_data.items():
            setattr(product, field, value)
        session.add(product)
        try:
            await session.commit()
        except IntegrityError as exc:
            await session.rollback()
            raise exc
        await session.refresh(product)
        return product

    async def delete_product(
        self,
        session: AsyncSession,
        product: Product,
    ) -> None:
        """Удалить продукт по ID."""
        await session.delete(product)
        await session.commit()


product_crud = ProductCRUD()
