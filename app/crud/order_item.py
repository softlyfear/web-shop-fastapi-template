"""OrderItem CRUD operations."""

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import BaseCrud
from app.models import OrderItem, Product
from app.schemas import OrderItemCreate, OrderItemUpdate


class OrderItemCrud(BaseCrud[OrderItem, OrderItemCreate, OrderItemUpdate]):
    """CRUD operations for OrderItem model."""

    async def get_by_order_id(
        self,
        session: AsyncSession,
        order_id: int,
    ) -> list[OrderItem]:
        """Get all order items."""
        stmt = select(OrderItem).where(OrderItem.order_id == order_id)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def create_with_validation(
        self,
        session: AsyncSession,
        obj_in: OrderItemCreate,
        order_id: int,
    ) -> OrderItem:
        """Create order item with stock validation."""
        product = await session.get(Product, obj_in.product_id)
        if not product:
            raise ValueError(f"Product with ID={obj_in.product_id} not found")

        if product.stock < obj_in.quantity:
            raise ValueError(
                f"Insufficient stock for {product.name}. "
                f"Available: {product.stock}, requested: {obj_in.quantity}"
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
        """Calculate order total price."""
        items = await self.get_by_order_id(session, order_id)
        return sum(item.price * item.quantity for item in items)


order_item_crud = OrderItemCrud(OrderItem)
