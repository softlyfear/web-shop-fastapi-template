from app.api.v1.router_factory import build_crud_router
from app.crud import order_crud
from app.schemas import OrderCreate, OrderRead, OrderUpdate

router = build_crud_router(
    crud=order_crud,
    create_schema=OrderCreate,
    update_schema=OrderUpdate,
    read_schema=OrderRead,
    resource_name="order",
)
