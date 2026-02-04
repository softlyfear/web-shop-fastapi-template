from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import BaseCrud
from app.models import OrderItem, Product
from app.schemas import OrderItemCreate, OrderItemUpdate


class OrderItemCrud(BaseCrud[OrderItem, OrderItemCreate, OrderItemUpdate]):
    async def get_by_order_id(
        self,
        session: AsyncSession,
        order_id: int,
    ) -> list[OrderItem]:
        """Получить все позиции заказа."""
        stmt = select(OrderItem).where(OrderItem.order_id == order_id)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def create_with_validation(
        self,
        session: AsyncSession,
        obj_in: OrderItemCreate,
        order_id: int,
    ) -> OrderItem:
        """Создать позицию заказа с проверкой наличия товара."""
        product = await session.get(Product, obj_in.product_id)
        if not product:
            raise ValueError(f"Продукт с ID={obj_in.product_id} не найден")

        if product.stock < obj_in.quantity:
            raise ValueError(
                f"Не достаточно товара на складе {product.name}. "
                f"Доступно: {product.stock}, запрошено: {obj_in.quantity}"
            )

        data = obj_in.model_dump()
        data["order_id"] = order_id
        if not data.get("price"):
            data["price"] = product.price

        obj = OrderItem(**data)
        session.add(obj)

        product.stock -= obj_in.quantity

        return await self._commit_refresh(session, obj)

    async def calculate_order_total(
        self,
        session: AsyncSession,
        order_id: int,
    ) -> Decimal:
        """Вычислить общую стоимость заказа."""
        items = await self.get_by_order_id(session, order_id)
        return sum(item.price * item.quantity for item in items)


order_item_crud = OrderItemCrud(OrderItem)
