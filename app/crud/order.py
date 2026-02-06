from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud import BaseCrud
from app.models import Order, OrderItem, OrderStatus
from app.schemas import OrderCreate, OrderUpdate


class OrderCrud(BaseCrud[Order, OrderCreate, OrderUpdate]):
    async def get_by_user_id(
        self,
        session: AsyncSession,
        user_id: int,
        offset: int = 0,
        limit: int = 25,
    ) -> list[Order]:
        """Получить все заказы пользователя."""
        stmt = (
            select(Order)
            .where(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_status(
        self,
        session: AsyncSession,
        status: OrderStatus,
        offset: int = 0,
        limit: int = 25,
    ) -> list[Order]:
        """Получить заказы по статусу."""
        stmt = (
            select(Order)
            .where(Order.status == status)
            .order_by(Order.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def get_with_items(
        self,
        session: AsyncSession,
        order_id: int,
    ) -> Order | None:
        """Получить заказ со всеми items и продуктами (eager loading)."""
        stmt = (
            select(Order)
            .where(Order.id == order_id)
            .options(selectinload(Order.items).selectinload(OrderItem.product))
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_status(
        self,
        session: AsyncSession,
        db_obj: Order,
        new_status: OrderStatus,
    ) -> Order:
        """Обновить статус заказа."""
        order = db_obj
        if new_status == OrderStatus.cancelled and db_obj.status == OrderStatus.pending:
            order_with_items = await self.get_with_items(session, db_obj.id)
            if order_with_items:
                order = order_with_items
                for item in order.items:
                    if item.product:
                        item.product.stock += item.quantity

        order.status = new_status
        return await self._commit_refresh(session, order)

    async def get_user_orders_by_status(
        self,
        session: AsyncSession,
        user_id: int,
        status: OrderStatus,
        offset: int = 0,
        limit: int = 25,
    ) -> list[Order]:
        """Получить заказы пользователя с определенным статусом."""
        stmt = (
            select(Order)
            .where(Order.user_id == user_id, Order.status == status)
            .order_by(Order.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def create_order_with_items(
        self,
        session: AsyncSession,
        user_id: int,
        shipping_address: str,
        cart_items: list[dict],
    ) -> Order:
        """
        Создать заказ со всеми позициями атомарно.

        Args:
            user_id: ID пользователя
            shipping_address: Адрес доставки
            cart_items: Список словарей с ключами: product_id, quantity, price

        Returns:
            Order: Созданный заказ

        Raises:
            ValueError: Если корзина пуста или товар недоступен
        """
        from app.crud import product_crud

        if not cart_items:
            raise ValueError("Корзина пуста")

        total_price = Decimal("0")
        validated_items = []

        for item in cart_items:
            product = await product_crud.get(session, item["product_id"])

            if not product:
                raise ValueError(f"Товар с ID {item['product_id']} не найден")

            if not product.is_active:
                raise ValueError(f"Товар '{product.name}' недоступен")

            if product.stock < item["quantity"]:
                raise ValueError(
                    f"Недостаточно товара '{product.name}' на складе. "
                    f"Доступно: {product.stock}, запрошено: {item['quantity']}"
                )

            item_price = Decimal(str(item["price"]))
            item_total = item_price * item["quantity"]
            total_price += item_total

            validated_items.append(
                {
                    "product": product,
                    "quantity": item["quantity"],
                    "price": item_price,
                }
            )

        order = Order(
            user_id=user_id,
            status=OrderStatus.pending,
            total_price=total_price,
            shipping_address=shipping_address,
        )
        session.add(order)
        await session.flush()

        for item_data in validated_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item_data["product"].id,
                quantity=item_data["quantity"],
                price=item_data["price"],
            )
            session.add(order_item)

            item_data["product"].stock -= item_data["quantity"]

        await session.commit()
        await session.refresh(order)

        return order


order_crud = OrderCrud(Order)
