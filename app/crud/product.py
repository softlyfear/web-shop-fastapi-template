from typing import List

from slugify import slugify
from sqlalchemy import select
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

        if not product_data.get("slug") or product_data["slug"] == "string":
            product_data["slug"] = slugify(product_data["name"])

        product = Product(**product_data)

        session.add(product)
        await session.commit()

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
    ) -> List[Product]:
        """Получить все продукты."""
        stmt = select(Product).offset(offset).limit(limit)
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

        if not update_data.get("slug") or update_data["slug"] == "string":
            update_data["slug"] = slugify(update_data["name"])

        for field, value in update_data.items():
            setattr(product, field, value)

        session.add(product)
        await session.commit()
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
