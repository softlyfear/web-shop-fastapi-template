from app.crud import BaseCrud
from app.models import Order
from app.schemas import OrderCreate, OrderUpdate


class OrderCrud(BaseCrud[Order, OrderCreate, OrderUpdate]):
    pass


order_crud = OrderCrud(Order)
