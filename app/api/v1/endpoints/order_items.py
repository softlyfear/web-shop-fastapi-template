from app.api.v1.router_factory import build_crud_router
from app.crud import order_item_crud
from app.schemas import OrderCreate, OrderItemRead, OrderItemUpdate

router = build_crud_router(
    crud=order_item_crud,
    create_schema=OrderCreate,
    update_schema=OrderItemUpdate,
    read_schema=OrderItemRead,
    resource_name="order_item",
)
