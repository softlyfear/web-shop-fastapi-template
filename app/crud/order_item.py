from app.crud import BaseCrud
from app.models import OrderItem
from app.schemas import OrderItemCreate, OrderItemUpdate


class OrderItemCrud(BaseCrud[OrderItem, OrderItemCreate, OrderItemUpdate]):
    pass


order_item_crud = OrderItemCrud(OrderItem)
