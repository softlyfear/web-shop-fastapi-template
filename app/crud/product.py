from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Product
from app.schemas import ProductCreate


async def create_product(session: AsyncSession, product_in: ProductCreate) -> Product:
    """Создать новый продукт."""
    product_data = product_in.model_dump()
    product = Product(**product_data)

    session.add(product)
    await session.commit()

    await session.refresh(product)
    return product
